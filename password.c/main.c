#include <stdio.h>
#include <stdint.h>
typedef unsigned long long ull;
typedef unsigned char u8;
#define X(a,b) ((a) ^ (b))
#define A(x) (1ULL << (x))
#define B(x) _p10(x)
#define S(x,y) ((x) * (y))
static const u8 _f4b7[] = { 0x5a ^ 1, 0x5a ^ 1, 0x5a ^ 1, 0x5a ^ 2, 0x5a ^ 2, 0x5a ^ 2 };
static const u8 _k3y = 0x5a;

static const char _bee[] = "r\n\nhi";
volatile int _8bc = 0xab0ff3a;
static ull _p10(unsigned n){
    ull _r = 1ULL;
    unsigned _i = 0;
    goto _enter;
_82e:
    _r *= 10ULL;
    _i++;
_enter:
    if(_i < n) goto _82e;
    return _r;
}


int main(void){
    ull _tot = 0ULL;
    unsigned _k = 0;
    char _noise[3] = {0,1,2};
    (void)_noise;
b2a:
    if(!(_k <= 6)) goto _ii3;
    unsigned _s = 0;
    unsigned _j = _k + 1;

c7f:
    if(!(_j <= 6)) goto _after_sum;
    unsigned _idx = (_j - 1);
    u8 _enc = _f4b7[_idx];
    u8 _val = X(_enc, _k3y);
    _s = ((_s ^ 0u) + (_val & 0xFFu));
    _j++;
    goto c7f;

_after_sum:
    ull _tw = A(_k ^ ( (unsigned)(_8bc & 0x7) ));
    if((_tw >> _k) != 1ULL){
        _tw = A(_k);
    }
    ull _ten = B(_s);
    ull _term = S(_tw, _ten);
    if((_term & 0x1) == 0){
        _tot += _term;
        goto _f30;
    } else {
        ull _tmp = ~_term;
        _tmp = ~_tmp;
        _tot += _tmp;
        goto _f30;
    }

_f30:
    _k = (unsigned)((_k + 1) ^ 0u);
    goto b2a;

_ii3:
    if((_8bc & 0xff) == 0x00) goto _print;
    goto _print;

_print:
    printf("%llu\n", _tot);
    return 0;
}