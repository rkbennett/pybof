// Need to define these to be able to use SetDllDirectory.
#define _WIN32_WINNT 0x0502
#define NTDDI_VERSION 0x05020000
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "APIResolve.h"
#include <windows.h>
#include "beacon_compatibility.h"

static char module_doc[] =
"Loader for BOF";
char builtin_name[] = "builtins";

#include "COFFLoader.h"

#ifndef STANDALONE
extern wchar_t dirname[]; // executable/dll directory
#endif

static PyObject *
run(PyObject *self, PyObject *args)
{
	char *bofArgs;
	char *function;
	size_t size;
	size_t argSize;
	int resp;
	int outdataSize = 0;
	char* outdata = NULL;
	unsigned char *data;


	if (!PyArg_ParseTuple(args, "ss#|z#",
			      &function, &data, &size, &bofArgs, &argSize))
		return NULL;
	
	resp = RunCOFF(function, data, size, bofArgs, argSize);
	if (resp == 0) {
		outdata = BeaconGetOutputData(&outdataSize);
		if (outdata != NULL) {
			return PyUnicode_FromString(outdata);
        }
	} 
	PyErr_WarnEx(PyExc_RuntimeError, "BOF had no return value", 1);
	return PyUnicode_FromString("");
}

static PyObject *
get_verbose_flag(PyObject *self, PyObject *args)
{
	return PyLong_FromLong(Py_VerboseFlag);
}

static PyMethodDef methods[] = {
	{ "run", run, METH_VARARGS,
	  "Loads and runs BOF function from memory" },
	{ NULL, NULL },		/* Sentinel */
};

static struct PyModuleDef moduledef = {
	PyModuleDef_HEAD_INIT,
	"_bof", /* m_name */
	module_doc, /* m_doc */
	-1, /* m_size */
	methods, /* m_methods */
	NULL, /* m_reload */
	NULL, /* m_traverse */
	NULL, /* m_clear */
	NULL, /* m_free */
};

PyMODINIT_FUNC PyInit__bof(void)
{
	return PyModule_Create(&moduledef);
};

INT APIENTRY DllMain(HMODULE hModule,
    DWORD  ul_reason_for_call,
    LPVOID lpReserved
)
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
		PyGILState_STATE gstate;
		gstate = PyGILState_Ensure();
        if (PyImport_AppendInittab("_bof", PyInit__bof) == -1) {
            fprintf(stderr, "Error: could not extend in-built modules table\n");
            exit(1);
        }
		Py_Initialize();
		PyObject *Module = PyInit__bof();
		PyObject *builtin_module = PyImport_ImportModule(builtin_name);
		PyModule_AddObject(builtin_module, "_bof", Module);
        PyGILState_Release(gstate);
        break;
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return 1;
}