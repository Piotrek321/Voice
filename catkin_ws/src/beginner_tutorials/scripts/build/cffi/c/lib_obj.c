
/* A Lib object is what is in the "lib" attribute of a C extension
   module originally created by recompile().

   A Lib object is special in the sense that it has a custom
   __getattr__ which returns C globals, functions and constants.  It
   raises AttributeError for anything else, even attrs like '__class__'.

   A Lib object has got a reference to the _cffi_type_context_s
   structure, which is used to create lazily the objects returned by
   __getattr__.
*/

struct CPyExtFunc_s {
    PyMethodDef md;
    void *direct_fn;
    int type_index;
};
static const char cpyextfunc_doc[] =
    "direct call to the C function of the same name";

struct LibObject_s {
    PyObject_HEAD
    builder_c_t *l_types_builder; /* same as the one on the ffi object */
    PyObject *l_dict;           /* content, built lazily */
    PyObject *l_libname;        /* some string that gives the name of the lib */
    FFIObject *l_ffi;           /* reference back to the ffi object */
    void *l_libhandle;          /* the dlopen()ed handle, if any */
};

static struct CPyExtFunc_s *_cpyextfunc_get(PyObject *x)
{
    struct CPyExtFunc_s *exf;

    if (!PyCFunction_Check(x))
        return NULL;
    if (!LibObject_Check(PyCFunction_GET_SELF(x)))
        return NULL;

    exf = (struct CPyExtFunc_s *)(((PyCFunctionObject *)x) -> m_ml);
    if (exf->md.ml_doc != cpyextfunc_doc)
        return NULL;

    return exf;
}

static PyObject *_cpyextfunc_type(LibObject *lib, struct CPyExtFunc_s *exf)
{
    PyObject *tuple, *result;
    tuple = realize_c_type_or_func(lib->l_types_builder,
                                   lib->l_types_builder->ctx.types,
                                   exf->type_index);
    if (tuple == NULL)
        return NULL;

    /* 'tuple' is a tuple of length 1 containing the real CT_FUNCTIONPTR
       object */
    result = PyTuple_GetItem(tuple, 0);
    Py_XINCREF(result);
    Py_DECREF(tuple);
    return result;
}

static PyObject *_cpyextfunc_type_index(PyObject *x)
{
    struct CPyExtFunc_s *exf;
    LibObject *lib;

    assert(PyErr_Occurred());
    exf = _cpyextfunc_get(x);
    if (exf == NULL)
        return NULL;    /* still the same exception is set */

    PyErr_Clear();

    lib = (LibObject *)PyCFunction_GET_SELF(x);
    return _cpyextfunc_type(lib, exf);
}

static void cdlopen_close_ignore_errors(void *libhandle);  /* forward */
static void *cdlopen_fetch(PyObject *libname, void *libhandle, char *symbol);

static void lib_dealloc(LibObject *lib)
{
    cdlopen_close_ignore_errors(lib->l_libhandle);
    Py_DECREF(lib->l_dict);
    Py_DECREF(lib->l_libname);
    Py_DECREF(lib->l_ffi);
    PyObject_Del(lib);
}

static int lib_traverse(LibObject *lib, visitproc visit, void *arg)
{
    Py_VISIT(lib->l_dict);
    Py_VISIT(lib->l_libname);
    Py_VISIT(lib->l_ffi);
    return 0;
}

static PyObject *lib_repr(LibObject *lib)
{
    return PyText_FromFormat("<Lib object for '%.200s'>",
                             PyText_AS_UTF8(lib->l_libname));
}

static PyObject *lib_build_cpython_func(LibObject *lib,
                                        const struct _cffi_global_s *g,
                                        const char *s, int flags)
{
    /* First make sure the argument types and return type are really
       built.  The C extension code can then assume that they are,
       by calling _cffi_type().
    */
    CTypeDescrObject *ct;
    struct CPyExtFunc_s *xfunc;
    int i, type_index = _CFFI_GETARG(g->type_op);
    _cffi_opcode_t *opcodes = lib->l_types_builder->ctx.types;

    if ((((uintptr_t)opcodes[type_index]) & 1) == 0) {
        /* the function type was already built.  No need to force
           the arg and return value to be built again. */
    }
    else {
        assert(_CFFI_GETOP(opcodes[type_index]) == _CFFI_OP_FUNCTION);

        /* return type: */
        ct = realize_c_type(lib->l_types_builder, opcodes,
                            _CFFI_GETARG(opcodes[type_index]));
        if (ct == NULL)
            return NULL;
        Py_DECREF(ct);

        /* argument types: */
        i = type_index + 1;
        while (_CFFI_GETOP(opcodes[i]) != _CFFI_OP_FUNCTION_END) {
            ct = realize_c_type(lib->l_types_builder, opcodes, i);
            if (ct == NULL)
                return NULL;
            Py_DECREF(ct);
            i++;
        }
    }

    /* xxx the few bytes of memory we allocate here leak, but it's a
       minor concern because it should only occur for CPYTHON_BLTN.
       There is one per real C function in a CFFI C extension module.
       CPython never unloads its C extension modules anyway.
    */
    xfunc = PyMem_Malloc(sizeof(struct CPyExtFunc_s));
    if (xfunc == NULL) {
        PyErr_NoMemory();
        return NULL;
    }
    memset((char *)xfunc, 0, sizeof(struct CPyExtFunc_s));
    assert(g->address);
    xfunc->md.ml_meth = (PyCFunction)g->address;
    xfunc->md.ml_flags = flags;
    xfunc->md.ml_name = g->name;
    xfunc->md.ml_doc = cpyextfunc_doc;
    xfunc->direct_fn = g->size_or_direct_fn;
    xfunc->type_index = type_index;

    return PyCFunction_NewEx(&xfunc->md, (PyObject *)lib, lib->l_libname);
}

static PyObject *lib_build_and_cache_attr(LibObject *lib, PyObject *name,
                                          int recursion)
{
    /* does not return a new reference! */
    PyObject *x;
    int index;
    const struct _cffi_global_s *g;
    CTypeDescrObject *ct;
    builder_c_t *types_builder = lib->l_types_builder;
    char *s = PyText_AsUTF8(name);
    if (s == NULL)
        return NULL;

    index = search_in_globals(&types_builder->ctx, s, strlen(s));
    if (index < 0) {

        if (types_builder->included_libs != NULL) {
            Py_ssize_t i;
            PyObject *included_ffis = types_builder->included_ffis;
            PyObject *included_libs = types_builder->included_libs;

            if (recursion > 100) {
                PyErr_SetString(PyExc_RuntimeError,
                    "recursion overflow in ffi.include() delegations");
                return NULL;
            }

            for (i = 0; i < PyTuple_GET_SIZE(included_libs); i++) {
                LibObject *lib1;

                lib1 = (LibObject *)PyTuple_GET_ITEM(included_libs, i);
                if (lib1 != NULL) {
                    x = PyDict_GetItem(lib1->l_dict, name);
                    if (x != NULL) {
                        Py_INCREF(x);
                        goto found;
                    }
                    x = lib_build_and_cache_attr(lib1, name, recursion + 1);
                    if (x != NULL) {
                        Py_INCREF(x);
                        goto found;
                    }
                }
                else {
                    FFIObject *ffi1;

                    ffi1 = (FFIObject *)PyTuple_GetItem(included_ffis, i);
                    if (ffi1 == NULL)
                        return NULL;
                    x = ffi_fetch_int_constant(ffi1, s, recursion + 1);
                    if (x != NULL)
                        goto found;
                }
                if (PyErr_Occurred())
                    return NULL;
            }
        }

        if (recursion > 0)
            return NULL;  /* no error set, continue looking elsewhere */

        PyErr_Format(PyExc_AttributeError,
                     "cffi library '%.200s' has no function, constant "
                     "or global variable named '%.200s'",
                     PyText_AS_UTF8(lib->l_libname), s);
        return NULL;
    }

    g = &types_builder->ctx.globals[index];

    switch (_CFFI_GETOP(g->type_op)) {

    case _CFFI_OP_CPYTHON_BLTN_V:
        x = lib_build_cpython_func(lib, g, s, METH_VARARGS);
        break;

    case _CFFI_OP_CPYTHON_BLTN_N:
        x = lib_build_cpython_func(lib, g, s, METH_NOARGS);
        break;

    case _CFFI_OP_CPYTHON_BLTN_O:
        x = lib_build_cpython_func(lib, g, s, METH_O);
        break;

    case _CFFI_OP_CONSTANT_INT:
    case _CFFI_OP_ENUM:
    {
        /* a constant integer whose value, in an "unsigned long long",
           is obtained by calling the function at g->address */
        x = realize_global_int(types_builder, index);
        break;
    }

    case _CFFI_OP_CONSTANT:
    case _CFFI_OP_DLOPEN_CONST:
    {
        /* a constant which is not of integer type */
        char *data;
        ct = realize_c_type(types_builder, types_builder->ctx.types,
                            _CFFI_GETARG(g->type_op));
        if (ct == NULL)
            return NULL;

        if (ct->ct_size <= 0) {
            PyErr_SetString(PyExc_SystemError, "constant has no known size");
            return NULL;
        }
        if (g->address == NULL) {
            /* for dlopen() style */
            assert(_CFFI_GETOP(g->type_op) == _CFFI_OP_DLOPEN_CONST);
            data = cdlopen_fetch(lib->l_libname, lib->l_libhandle, s);
            if (data == NULL)
                return NULL;
        }
        else {
            /* xxx the few bytes of memory we allocate here leak, but it's
               a minor concern because it should only occur for
               OP_CONSTANT.  There is one per real non-integer C constant
               in a CFFI C extension module.  CPython never unloads its C
               extension modules anyway.  Note that we used to do alloca(),
               but see issue #198. */
            assert(_CFFI_GETOP(g->type_op) == _CFFI_OP_CONSTANT);
            data = PyMem_Malloc(ct->ct_size);
            if (data == NULL) {
                PyErr_NoMemory();
                return NULL;
            }
            ((void(*)(char*))g->address)(data);
        }
        x = convert_to_object(data, ct);
        Py_DECREF(ct);
        break;
    }

    case _CFFI_OP_GLOBAL_VAR:
    {
        /* global variable of the exact type specified here */
        Py_ssize_t g_size = (Py_ssize_t)g->size_or_direct_fn;
        ct = realize_c_type(types_builder, types_builder->ctx.types,
                            _CFFI_GETARG(g->type_op));
        if (ct == NULL)
            return NULL;
        if (g_size != ct->ct_size && g_size != 0 && ct->ct_size > 0) {
            PyErr_Format(FFIError,
                         "global variable '%.200s' should be %zd bytes "
                         "according to the cdef, but is actually %zd",
                         s, ct->ct_size, g_size);
            x = NULL;
        }
        else {
            void *address = g->address;
            if (address == NULL) {
                /* for dlopen() style */
                address = cdlopen_fetch(lib->l_libname, lib->l_libhandle, s);
                if (address == NULL)
                    return NULL;
            }
            x = make_global_var(ct, address);
        }
        Py_DECREF(ct);
        break;
    }

    case _CFFI_OP_DLOPEN_FUNC:
    {
        /* For dlopen(): the function of the given 'name'.  We use
           dlsym() to get the address of something in the dynamic
           library, which we interpret as being exactly a function of
           the specified type.
        */
        PyObject *ct1;
        void *address = cdlopen_fetch(lib->l_libname, lib->l_libhandle, s);
        if (address == NULL)
            return NULL;

        ct1 = realize_c_type_or_func(types_builder,
                                     types_builder->ctx.types,
                                     _CFFI_GETARG(g->type_op));
        if (ct1 == NULL)
            return NULL;

        assert(!CTypeDescr_Check(ct1));   /* must be a function */
        x = new_simple_cdata(address, unwrap_fn_as_fnptr(ct1));

        Py_DECREF(ct1);
        break;
    }

    default:
        PyErr_Format(PyExc_NotImplementedError, "in lib_build_attr: op=%d",
                     (int)_CFFI_GETOP(g->type_op));
        return NULL;
    }

 found:
    if (x != NULL) {
        int err = PyDict_SetItem(lib->l_dict, name, x);
        Py_DECREF(x);
        if (err < 0)     /* else there is still one ref left in the dict */
            return NULL;
    }
    return x;
}

#define LIB_GET_OR_CACHE_ADDR(x, lib, name, error)      \
    do {                                                \
        x = PyDict_GetItem(lib->l_dict, name);          \
        if (x == NULL) {                                \
            x = lib_build_and_cache_attr(lib, name, 0); \
            if (x == NULL) {                            \
                error;                                  \
            }                                           \
        }                                               \
    } while (0)

static PyObject *lib_getattr(LibObject *lib, PyObject *name)
{
    PyObject *x;
    LIB_GET_OR_CACHE_ADDR(x, lib, name, return NULL);

    if (GlobSupport_Check(x)) {
        return read_global_var((GlobSupportObject *)x);
    }
    Py_INCREF(x);
    return x;
}

static int lib_setattr(LibObject *lib, PyObject *name, PyObject *val)
{
    PyObject *x;
    LIB_GET_OR_CACHE_ADDR(x, lib, name, return -1);

    if (val == NULL) {
        PyErr_SetString(PyExc_AttributeError, "C attribute cannot be deleted");
        return -1;
    }

    if (GlobSupport_Check(x)) {
        return write_global_var((GlobSupportObject *)x, val);
    }

    PyErr_Format(PyExc_AttributeError,
                 "cannot write to function or constant '%.200s'",
                 PyText_Check(name) ? PyText_AS_UTF8(name) : "?");
    return -1;
}

static PyObject *lib_dir(LibObject *lib, PyObject *noarg)
{
    const struct _cffi_global_s *g = lib->l_types_builder->ctx.globals;
    int i, total = lib->l_types_builder->ctx.num_globals;
    PyObject *lst = PyList_New(total);
    if (lst == NULL)
        return NULL;

    for (i = 0; i < total; i++) {
        PyObject *s = PyText_FromString(g[i].name);
        if (s == NULL) {
            Py_DECREF(lst);
            return NULL;
        }
        PyList_SET_ITEM(lst, i, s);
    }
    return lst;
}

static PyMethodDef lib_methods[] = {
    {"__dir__",   (PyCFunction)lib_dir,  METH_NOARGS},
    {NULL,        NULL}           /* sentinel */
};

static PyTypeObject Lib_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "CompiledLib",
    sizeof(LibObject),
    0,
    (destructor)lib_dealloc,                    /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_compare */
    (reprfunc)lib_repr,                         /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    (getattrofunc)lib_getattr,                  /* tp_getattro */
    (setattrofunc)lib_setattr,                  /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                         /* tp_flags */
    0,                                          /* tp_doc */
    (traverseproc)lib_traverse,                 /* tp_traverse */
    0,                                          /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    0,                                          /* tp_iter */
    0,                                          /* tp_iternext */
    lib_methods,                                /* tp_methods */
    0,                                          /* tp_members */
    0,                                          /* tp_getset */
    0,                                          /* tp_base */
    0,                                          /* tp_dict */
    0,                                          /* tp_descr_get */
    0,                                          /* tp_descr_set */
    offsetof(LibObject, l_dict),                /* tp_dictoffset */
};

static LibObject *lib_internal_new(FFIObject *ffi, char *module_name,
                                   void *dlopen_libhandle)
{
    LibObject *lib;
    PyObject *libname, *dict;

    libname = PyText_FromString(module_name);
    if (libname == NULL)
        goto err1;

    dict = PyDict_New();
    if (dict == NULL)
        goto err2;

    lib = PyObject_New(LibObject, &Lib_Type);
    if (lib == NULL)
        goto err3;

    lib->l_types_builder = &ffi->types_builder;
    lib->l_dict = dict;
    lib->l_libname = libname;
    Py_INCREF(ffi);
    lib->l_ffi = ffi;
    lib->l_libhandle = dlopen_libhandle;
    return lib;

 err3:
    Py_DECREF(dict);
 err2:
    Py_DECREF(libname);
 err1:
    cdlopen_close_ignore_errors(dlopen_libhandle);
    return NULL;
}

static PyObject *address_of_global_var(PyObject *args)
{
    LibObject *lib;
    PyObject *x, *o_varname;
    char *varname;

    if (!PyArg_ParseTuple(args, "O!s", &Lib_Type, &lib, &varname))
        return NULL;

    /* rebuild a string from 'varname', to do typechecks and to force
       a unicode back to a plain string (on python 2) */
    o_varname = PyText_FromString(varname);
    if (o_varname == NULL)
        return NULL;

    LIB_GET_OR_CACHE_ADDR(x, lib, o_varname, goto error);
    Py_DECREF(o_varname);
    if (GlobSupport_Check(x)) {
        return cg_addressof_global_var((GlobSupportObject *)x);
    }
    else {
        struct CPyExtFunc_s *exf = _cpyextfunc_get(x);
        if (exf != NULL) {  /* an OP_CPYTHON_BLTN: '&func' returns a cdata */
            PyObject *ct;
            if (exf->direct_fn == NULL) {
                Py_INCREF(x);    /* backward compatibility */
                return x;
            }
            ct = _cpyextfunc_type(lib, exf);
            if (ct == NULL)
                return NULL;
            x = new_simple_cdata(exf->direct_fn, (CTypeDescrObject *)ct);
            Py_DECREF(ct);
            return x;
        }
        if (CData_Check(x) &&  /* a constant functionptr cdata: 'f == &f' */
                (((CDataObject *)x)->c_type->ct_flags & CT_FUNCTIONPTR) != 0) {
            Py_INCREF(x);
            return x;
        }
        else {
            PyErr_Format(PyExc_AttributeError,
                         "cannot take the address of the constant '%.200s'",
                         varname);
            return NULL;
        }
    }

 error:
    Py_DECREF(o_varname);
    return NULL;
}
