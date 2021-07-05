//The Python3 interface to libbf
#include <Python.h>
#include <math.h>
#include <string.h>
#include <stdio.h>
#include "libbf.h"

typedef enum {
	PYBF_CONST_PI,
	PYBF_OP_MUL,
	PYBF_OP_ADD,
	PYBF_OP_SUB,
	PYBF_OP_RINT,
	PYBF_OP_ROUND,
	PYBF_OP_CMP_EQ,
	PYBF_OP_CMP_LT,
	PYBF_OP_CMP_LE,
	PYBF_OP_DIV,
	PYBF_OP_FMOD,
	PYBF_OP_REM,
	PYBF_OP_SQRT,
	PYBF_OP_OR,
	PYBF_OP_XOR,
	PYBF_OP_AND,
	PYBF_OP_EXP,
	PYBF_OP_LOG,
	PYBF_OP_COS,
	PYBF_OP_SIN,
	PYBF_OP_TAN,
	PYBF_OP_ATAN,
	PYBF_OP_ATAN2,
	PYBF_OP_ASIN,
	PYBF_OP_ACOS,
	PYBF_OP_POW
} opEnum_t;

/* number of bits per base 10 digit */
#define BITS_PER_DIGIT 3.32192809488736234787

static bf_context_t bf_ctx;
static bf_t bf_A;
static bf_t bf_B;
static bf_t bf_X;

static void *my_bf_realloc(void *opaque, void *ptr, size_t size) {
    return realloc(ptr, size);
}

static PyObject* initialize (PyObject* self) {
	bf_context_init(&bf_ctx, my_bf_realloc, NULL);
    bf_init(&bf_ctx, &bf_A);
    bf_init(&bf_ctx, &bf_B);
    bf_init(&bf_ctx, &bf_X);

	//printf ("initialize: bf_A pointer is %d\n", (int64_t)(&bf_A));

	return Py_BuildValue("s", "Hello, Python with LibBF intialized!");
}

static PyObject* bf_op (PyObject* self, PyObject *args) {
	opEnum_t op;
	char *a;
	char *b;
	char *r_str;
    int64_t prec10;
	int status;
	limb_t prec;

	if (!PyArg_ParseTuple(args, "Liss", &prec10, &op, &a, &b)) {
		return NULL;
	}
	prec = (limb_t) BITS_PER_DIGIT * (prec10 + 14) * (1.3);
	//printf ("Got %s and %s from Python\n", a, b);
	//printf ("bf_op: bf_A pointer is %d\n", (int64_t)(&bf_A));
	bf_atof(&bf_A, a, NULL, 10, prec, BF_RNDZ);
	bf_atof(&bf_B, b, NULL, 10, prec, BF_RNDZ);
	switch (op) {
		case PYBF_OP_MUL: bf_mul(&bf_X, &bf_A, &bf_B, prec, BF_RNDZ); break;
		case PYBF_OP_ADD: bf_add(&bf_X, &bf_A, &bf_B, prec, BF_RNDZ); break;
		case PYBF_OP_SUB: bf_sub(&bf_X, &bf_A, &bf_B, prec, BF_RNDZ); break;
		case PYBF_OP_RINT: bf_set (&bf_X, &bf_A); bf_rint(&bf_X, BF_RNDZ); break;
		case PYBF_OP_ROUND: bf_set (&bf_X, &bf_A); bf_round(&bf_X, prec, BF_RNDZ); break;
		case PYBF_OP_CMP_EQ: status = bf_cmp_eq(&bf_A, &bf_B); break;
		case PYBF_OP_CMP_LT: status = bf_cmp_lt(&bf_A, &bf_B); break;
		case PYBF_OP_CMP_LE: status = bf_cmp_le(&bf_A, &bf_B); break;
		case PYBF_OP_DIV: bf_div(&bf_X, &bf_A, &bf_B, prec, BF_RNDZ); break;
		case PYBF_OP_FMOD: bf_rem(&bf_X, &bf_A, &bf_B, prec, BF_RNDZ, BF_RNDZ); break;
		case PYBF_OP_REM: bf_rem(&bf_X, &bf_A, &bf_B, prec, BF_RNDZ, BF_RNDZ); break;
		case PYBF_OP_SQRT: bf_sqrt(&bf_X, &bf_A, prec, BF_RNDZ); break;
		case PYBF_OP_OR: bf_logic_or(&bf_X, &bf_A,  &bf_B); break;
		case PYBF_OP_XOR: bf_logic_xor(&bf_X, &bf_A, &bf_B); break;
		case PYBF_OP_AND: bf_logic_and(&bf_X, &bf_A, &bf_B); break;
		case PYBF_OP_EXP: bf_exp(&bf_X, &bf_A, prec, BF_RNDZ); break;
		case PYBF_OP_LOG: bf_log(&bf_X, &bf_A, prec, BF_RNDZ); break;
		case PYBF_OP_COS: bf_cos(&bf_X, &bf_A, prec, BF_RNDZ); break;
		case PYBF_OP_SIN: bf_sin(&bf_X, &bf_A, prec, BF_RNDZ); break;
		case PYBF_OP_TAN: bf_tan(&bf_X, &bf_A, prec, BF_RNDZ); break;
		case PYBF_OP_ATAN: bf_atan(&bf_X, &bf_A, prec, BF_RNDZ); break;
		case PYBF_OP_ATAN2: bf_atan2(&bf_X, &bf_A, &bf_B, prec, BF_RNDZ); break;
		case PYBF_OP_ACOS: bf_acos(&bf_X, &bf_A, prec, BF_RNDZ); break;
		case PYBF_OP_ASIN: bf_asin(&bf_X, &bf_A, prec, BF_RNDZ); break;
		case PYBF_OP_POW: bf_pow(&bf_X, &bf_A, &bf_B, prec, BF_RNDZ); break;
		case PYBF_CONST_PI: bf_const_pi(&bf_B, prec, BF_RNDZ);
			bf_mul(&bf_X, &bf_A, &bf_B, prec, BF_RNDZ);
			break;
		default: bf_const_pi(&bf_X, prec, BF_RNDZ); break;
	}

	if ((op == PYBF_OP_CMP_EQ) || (op == PYBF_OP_CMP_EQ) || (op == PYBF_OP_CMP_EQ)) {
		if (status == 0)
			bf_atof(&bf_X, "0", NULL, 10, prec, BF_RNDZ);
		else
			bf_atof(&bf_X, "1", NULL, 10, prec, BF_RNDZ);
	}	
	//printf ("bf_op: prec is %d\n", prec);
	//printf ("bf_op: prec10 is %ld\n", (limb_t)prec10);
	r_str = bf_ftoa(NULL, &bf_X, 10, (limb_t)prec10, BF_RNDZ);

	return Py_BuildValue("s", r_str);
}

static PyObject* cleanup (PyObject* self) {
    bf_delete(&bf_A);
    bf_delete(&bf_B);
    bf_delete(&bf_X);
	bf_context_end(&bf_ctx);

	return Py_BuildValue("s", "Python with LibBF cleaned up!");
}

static char pybf_initialize_docs[] =
   "initialize(): Python with LibBF initialize function\n";

static char pybf_bf_op_docs[] =
   "bf_op(): Python with LibBF bf_op function\n";

static char pybf_cleanup_docs[] =
   "cleanup( ): Python with LibBF cleanup function\n";

static PyMethodDef pybf_methods[] = {
	{"initialize", (PyCFunction)initialize, 
      METH_NOARGS, pybf_initialize_docs},
	{"bf_op", (PyCFunction)bf_op, 
      METH_VARARGS, pybf_bf_op_docs},
	{"cleanup", (PyCFunction)cleanup, 
      METH_NOARGS, pybf_cleanup_docs},
	{ NULL, NULL, 0, NULL }
};

static struct PyModuleDef pybf = {
    PyModuleDef_HEAD_INIT,
    "PyBF", /* name of module */
    "Extension module for LibBF!\n", /* module documentation, may be NULL */
    -1,   /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
    pybf_methods
};

PyMODINIT_FUNC PyInit_pybf(void) {
    return PyModule_Create(&pybf);
}
