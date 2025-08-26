from typing import List

# ------------------ Issue 1: Implementar la función de suma ------------------
def _sumar(nums: List[float]) -> float:
    total = 0.0
    for n in nums:
        total += n
    return total

# ------------------ Issue 2: Implementar la función de resta ------------------
def _restar(nums: List[float]) -> float:
    if not nums:
        return 0.0
    res = nums[0]
    for n in nums[1:]:
        res -= n
    return res

# -------------- Issue 3: Implementar la función de multiplicación -------------
def _multiplicar(nums: List[float]) -> float:
    res = 1.0
    for n in nums:
        res *= n
    return res

# ---------------- Issue 4: Implementar la función de división -----------------
def _dividir(nums: List[float]) -> float:
    if not nums:
        return 0.0
    res = nums[0]
    for n in nums[1:]:
        if n == 0:
            raise ZeroDivisionError("División por cero")
        res /= n
    return res

# ------------------------ Análisis léxico (tokenización) ----------------------
def _tokenize(expr: str) -> List[str]:
    """
    Convierte ' -2.5 + 3*(4-1) ' en tokens como:
    ['-2.5', '+', '3', '*', '(', '4', '-', '1', ')']
    Errores:
      - vacío -> ValueError
      - carácter inválido -> ValueError
      - signo unario sin número -> SyntaxError
      - número con dos puntos decimales -> ValueError
    """
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

        # signo unario (+/-) si es inicio o va tras operador/(
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
            tokens.append(s[i:k])  # incluye el signo
            i = k
            continue

        # número (entero/decimal)
        if is_num_char(c):
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

        # operadores y paréntesis
        if c in ops:
            tokens.append(c)
            i += 1
            continue

        # cualquier otra cosa es inválida
        raise ValueError(f"Carácter inválido: '{c}'")
    return tokens

# -------------- Shunting–Yard: infijo -> RPN (respeta paréntesis) -------------
def _to_rpn(tokens: List[str]) -> List[str]:
    prec = {"+": 1, "-": 1, "*": 2, "/": 2}
    out: List[str] = []
    st: List[str] = []
    last = None  # chequeo de sintaxis simple

    for t in tokens:
        if t not in prec and t not in ("(", ")"):
            out.append(t)     # número
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
            st.pop()  # saca '('
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

# --------------------------- Evaluación de la RPN -----------------------------
def _eval_rpn(rpn: List[str]) -> float:
    st: List[float] = []
    for t in rpn:
        if t not in {"+", "-", "*", "/"}:
            st.append(float(t))
            continue

        if len(st) < 2:
            raise SyntaxError("Faltan operandos")
        b = st.pop()
        a = st.pop()

        # Issue 1: suma
        if t == "+":
            st.append(_sumar([a, b]))
            continue
        # Issue 2: resta
        if t == "-":
            st.append(_restar([a, b]))
            continue
        # Issue 3: multiplicación
        if t == "*":
            st.append(_multiplicar([a, b]))
            continue
        # Issue 4: división
        if t == "/":
            st.append(_dividir([a, b]))
            continue

    if len(st) != 1:
        raise SyntaxError("Expresión inválida")
    return st[0]

# ------------------------------- API pública ----------------------------------
def calculate(expr: str):
    """
    Interfaz principal:
      - expr: string como '2 + 3 * (4 - 1)'
      - ValueError: vacío / carácter inválido / número mal formado
      - SyntaxError: expresión incompleta, paréntesis mal cerrados, etc.
    Devuelve int si el resultado es entero exacto; en otro caso, float.
    """
    tokens = _tokenize(expr)
    rpn = _to_rpn(tokens)
    res = _eval_rpn(rpn)
    return int(res) if float(res).is_integer() else res

