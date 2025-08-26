# -*- coding: utf-8 -*-
from typing import List, Union
from decimal import Decimal, getcontext, ROUND_HALF_EVEN

# Precisión amplia para operaciones decimales (ajusta si tu profe pide otra)
getcontext().prec = 50
getcontext().rounding = ROUND_HALF_EVEN

Number = Union[int, Decimal]

# ------------------ Issue 1: Suma ------------------
def _sumar(nums: List[Number]) -> Number:
    acc: Number = 0
    for x in nums:
        acc = _op_add(acc, x)
    return acc

# ------------------ Issue 2: Resta ------------------
def _restar(nums: List[Number]) -> Number:
    if not nums:
        return 0
    acc: Number = nums[0]
    for x in nums[1:]:
        acc = _op_sub(acc, x)
    return acc

# -------------- Issue 3: Multiplicación -------------
def _multiplicar(nums: List[Number]) -> Number:
    acc: Number = 1
    for x in nums:
        acc = _op_mul(acc, x)
    return acc

# ---------------- Issue 4: División -----------------
def _dividir(nums: List[Number]) -> Number:
    if not nums:
        return 0
    acc: Number = nums[0]
    for x in nums[1:]:
        acc = _op_div(acc, x)
    return acc

# ===== Operadores con promoción de tipos (int <-> Decimal) =====

def _to_decimal(x: Number) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(x)

def _promote(a: Number, b: Number, force_decimal: bool = False) -> (Number, Number, bool):
    """
    Reglas:
      - Si alguno es Decimal -> ambos a Decimal.
      - En división -> siempre Decimal.
      - En +, -, * -> si ambos int -> int; si alguno Decimal -> Decimal.
    """
    if force_decimal or isinstance(a, Decimal) or isinstance(b, Decimal):
        return _to_decimal(a), _to_decimal(b), True
    return a, b, False

def _op_add(a: Number, b: Number) -> Number:
    a2, b2, dec = _promote(a, b)
    return a2 + b2

def _op_sub(a: Number, b: Number) -> Number:
    a2, b2, dec = _promote(a, b)
    return a2 - b2

def _op_mul(a: Number, b: Number) -> Number:
    a2, b2, dec = _promote(a, b)
    return a2 * b2

def _op_div(a: Number, b: Number) -> Number:
    if (isinstance(b, int) and b == 0) or (isinstance(b, Decimal) and b == 0):
        raise ZeroDivisionError("División por cero")
    a2, b2, _ = _promote(a, b, force_decimal=True)  # división siempre Decimal
    return a2 / b2

# ================= Tokenización =================
def _tokenize(expr: str) -> List[str]:
    if expr is None:
        raise ValueError("Expresión vacía")
    s = expr.replace(" ", "")
    if not s:
        raise ValueError("Expresión vacía")

    digits = set("0123456789")
    ops = set("+-*/()")
    tokens: List[str] = []
    i = 0

    def is_num_char(c: str) -> bool:
        return (c in digits) or c == "."

    while i < len(s):
        c = s[i]

        # signo unario (+/-) al inicio o tras operador/(
        if c in "+-" and (i == 0 or s[i - 1] in "+-*/("):
            j = i + 1
            if j >= len(s) or not is_num_char(s[j]):
                raise SyntaxError("Signo unario sin número")
            k = j
            dot = 0
            while k < len(s) and is_num_char(s[k]):
                if s[k] == ".":
                    dot += 1
                    if dot > 1:
                        raise ValueError("Número mal formado")
                k += 1
            tokens.append(s[i:k])  # número con signo
            i = k
            continue

        # número (int/decimal)
        if c.isdigit() or c == ".":
            j = i
            dot = 0
            while j < len(s) and is_num_char(s[j]):
                if s[j] == ".":
                    dot += 1
                    if dot > 1:
                        raise ValueError("Número mal formado")
                j += 1
            tokens.append(s[i:j])
            i = j
            continue

        # operadores / paréntesis
        if c in ops:
            tokens.append(c)
            i += 1
            continue

        raise ValueError(f"Carácter inválido: '{c}'")
    return tokens

# ========== Shunting–Yard (respeta precedencia y paréntesis) ==========
def _to_rpn(tokens: List[str]) -> List[str]:
    prec = {"+": 1, "-": 1, "*": 2, "/": 2}
    out: List[str] = []
    st: List[str] = []
    last = None

    for t in tokens:
        if t not in prec and t not in ("(", ")"):
            out.append(t)
            last = "num"
            continue

        if t in prec:
            if last in (None, "op", "("):
                raise SyntaxError("Operador en posición inválida")
            while st and st[-1] in prec and prec[st[-1]] >= prec[t]:
                out.append(st.pop())
            st.append(t)
            last = "op"
            continue

        if t == "(":
            st.append(t)
            last = "("
            continue

        if t == ")":
            if last in (None, "op", "("):
                raise SyntaxError("Paréntesis de cierre inválido")
            while st and st[-1] != "(":
                out.append(st.pop())
            if not st:
                raise SyntaxError("Paréntesis desbalanceados")
            st.pop()
            last = "num"
            continue

    if last in (None, "op", "("):
        raise SyntaxError("Expresión incompleta")

    while st:
        top = st.pop()
        if top in ("(", ")"):
            raise SyntaxError("Paréntesis desbalanceados")
        out.append(top)

    return out

# ================= Evaluación de la RPN =================
def _parse_number(tok: str) -> Number:
    # Si tiene punto -> Decimal (evita pérdida y 6.6000000000000005)
    if "." in tok:
        # Nota: Decimal(tok) con 'tok' tal cual (string) para exactitud
        return Decimal(tok)
    # si no, int (maneja enteros gigantes sin pérdida)
    return int(tok)

def _eval_rpn(rpn: List[str]) -> Number:
    st: List[Number] = []
    for t in rpn:
        if t not in {"+", "-", "*", "/"}:
            st.append(_parse_number(t))
            continue

        if len(st) < 2:
            raise SyntaxError("Faltan operandos")
        b = st.pop()
        a = st.pop()

        if t == "+":
            st.append(_op_add(a, b))
            continue
        if t == "-":
            st.append(_op_sub(a, b))
            continue
        if t == "*":
            st.append(_op_mul(a, b))
            continue
        if t == "/":
            st.append(_op_div(a, b))
            continue

    if len(st) != 1:
        raise SyntaxError("Expresión inválida")
    return st[0]

# ================= API pública =================
def calculate(expr: str):
    tokens = _tokenize(expr)
    rpn = _to_rpn(tokens)
    res = _eval_rpn(rpn)

    # Normaliza salida: si Decimal y es entero exacto -> int; si no -> float limpio
    if isinstance(res, Decimal):
        if res == res.to_integral_value():
            return int(res)
        # convertir a float para cumplir tests que comparan con literales float
        return float(res)
    else:
        # res es int
        return res


