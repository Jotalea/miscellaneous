#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char *f;
} E;

typedef struct {
    int l;
} C;

typedef struct {
    C *d;
    int n;
} X;

void init_E(E *e, char *f) {
    e->f = f;
}

char* e_func(E *e) {
    return e->f;
}

void init_C(C *c, int l) {
    c->l = l;
}

int i_func(C *c) {
    return ++(c->l);
}

void init_X(X *x, int n) {
    x->d = (C *)malloc(n * sizeof(C));
    x->n = n;
    for (int i = 0; i < n; ++i) {
        init_C(&(x->d[i]), i);
    }
}

int p_func(X *x) {
    while (1) {
        int all_done = 1;
        for (int j = 0; j < x->n; ++j) {
            if (x->d[j].l < 10) {
                all_done = 0;
                i_func(&(x->d[j]));
            }
        }
        if (all_done) break;
    }
    int sum = 0;
    for (int k = 0; k < x->n; ++k) {
        sum += x->d[k].l;
    }
    return sum;
}

const char* m(char *f, int n) {
    E e;
    init_E(&e, f);
    X x;
    init_X(&x, n);
    if (p_func(&x) > 50) {
        return e_func(&e);
    }
    return "O_o";
}

char* cl() {
    int v[] = {73, 32, 108, 111, 118, 101, 32, 121, 111, 117};
    static char s[20];
    s[0] = '\0';
    for (int i = 0; i < sizeof(v) / sizeof(v[0]); i++) {
        char c = (char)v[i];
        strncat(s, (char[]){c, '\0'}, 1);
    }
    return s;
}

int main() {
    const char* result = m(cl(), sizeof(cl()) - 1);
    printf("%s\n", result);
    X x;
    init_X(&x, sizeof(cl()) - 1);
    free(x.d);
    return 0;
}