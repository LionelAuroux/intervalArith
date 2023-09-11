from itvArith.itv import *
import logging

log = logging.getLogger(__name__)

class Val:
    """
    Value Declaration
    """
    def __init__(self, value, t=None):
        self._type = t
        self._value = value

    def __repr__(self):
        return f"{self._value}:{self._type}"

class Var:
    """
    Variable declaration
    """
    def __init__(self, name, value, t=None):
        self._name = name
        self._value = value
        self._type = t

    def __repr__(self):
        return f"{self._name} = {self._value}:{self._type}"

class Fun:
    """
    Function declaration
    """
    def __init__(self, name, *types):
        self._name = name
        #FIXME: rajouter le traitement des noms de paramètres et valeur par défaut
        self._types = types

    def __repr__(self):
        lr = [repr(it) for it in self._types[1:]]
        return f"fun {self._name}({', '.join(lr)}) -> {self._types[0]}"

class FunExpr:
    """
    Function call expression
    """
    def __init__(self, name, *params):
        self._name = name
        self._params = list(params)

    def add(self, param):
        self._params.append(param)

    def __repr__(self):
        lr = [repr(it) for it in self._params[1:]]
        txt = "()"
        if len(self._params):
            txt = f"({', '.join(lr)}) : {self._params[0]}"
        return f"{self._name}{txt}"

class AltTypeExpr:
    """
    Type alternatives
    """
    def __init__(self):
        self._alt = []

    def add(self, alt):
        self._alt.append(alt)

    def __repr__(self):
        lr = [repr(it) for it in self._alt]
        return f"({'^'.join(lr)})"

class Def:
    def __init__(self, name=None, t=None, **kw):
        """
        Définition d'une fonction
        """
        self._name = name
        self._type = t
        self._decls = {}
        #FIXME: le cache de typevar devrais être par résolution de fonction
        self._typevars = {}
        self.add_defs(kw)

    def globals(self, **kw):
        """
        Déclaration globales visible dans le block
        """
        self.add_defs(kw)
        return self

    def add_defs(self, kw):
        for v in kw.values():
            if hasattr(v, "_name"):
                log.info(f"NAME {v._name}")
                # handle overloading
                if v._name not in self._decls:
                    self._decls[v._name] = []
                log.info(f"Decl {v._name} in context {id(self._decls)}")
                self._decls[v._name].append(v)

    def block(self, stmts) -> 'Decl':
        self._stmts = stmts
        return self

    def assoc_left(self, p_cand, p_expr):
        if not p_cand._name in self._typevars:
            self._typevars[p_cand._name] = p_expr
        log.warning(f"{p_cand._name}=={self._typevars[p_cand._name]}")
        return self._typevars[p_cand._name]

    def assoc_right(self, p_cand, p_expr):
        if not p_expr._name in self._typevars:
            self._typevars[p_expr._name] = p_cand
        log.warning(f"{p_expr._name}=={self._typevars[p_expr._name]}")
        return self._typevars[p_expr._name]

    def get_fname(self, item):
        match item:
            case str():
                return item
            case FunExpr():
                return item._name
            case _:
                raise RuntimeError(f"Failed to match {type(item)} to get fname")

    def check_ctor(self, p_cand, p_expr):
        """
        Typage nomminatif, les 2 types sont identiques ou il existe une conversion possible de l'un vers l'autre via un constructeur
        ou une relation de covariance
        """
        if p_cand._name == p_expr._name:
            return p_cand.copy()
        raise RuntimeError(f"Can't find CTOR {type(p_expr)} to {type(p_cand)}")

    def check_itv(self, p_cand, p_expr):
        """
        Coerce interval d'entier
        """
        # covariance des intervales
        if p_expr <= p_cand:
            return p_cand.copy()
        raise RuntimeError(f"Can't coerce {type(p_expr)} and {type(p_cand)}")

    def check_intersect_left(self, p_cand, p_expr):
        """
        Intersection de la gauche avec un ensemble de type à droite
        """
        raise RuntimeError(f"Can't coerce {type(p_expr)} and {type(p_cand)}")

    def check_intersect_right(self, p_cand, p_expr):
        """
        Intersection un ensemble de type à gauche et un type à droite
        """
        raise RuntimeError(f"Can't coerce {type(p_expr)} and {type(p_cand)}")

    def check_intersect(self, p_cand, p_expr):
        """
        Intersection 2 ensembles de type
        """
        raise RuntimeError(f"Can't coerce {type(p_expr)} and {type(p_cand)}")

    def check_param(self, p_cand, p_expr):
        log.warning(f"?? {p_cand} // {p_expr}")
        match p_cand:
            case TypeVar():
                # FIXME
                # on coerce avec un type générique donc on "prends" le type de p_expr (BottomUp)
                return self.assoc_left(p_cand, p_expr)
            case TypeNamed():
                match p_expr:
                    case TypeVar():
                        # FIXME
                        # on coerce avec un type générique donc on "prends" le type de p_cand (TopDown)
                        return self.assoc_right(p_cand, p_expr)
                    case TypeNamed():
                        # check s'il existe un constructeur t1 > t2
                        return self.check_ctor(p_cand, p_expr)
                    case AltTypeExpr():
                        # intersection un type nommé avec un ensemble
                        return self.check_intersect_left(p_cand, p_expr)
            case itvInt():
                match p_expr:
                    case TypeVar():
                        # FIXME
                        # on coerce avec un type générique donc on "prends" le type de p_cand (TopDown)
                        return self.assoc_right(p_cand, p_expr)
                    case itvInt():
                        # FIXME coerce interval
                        return self.check_itv(p_cand, p_expr)
                    case AltTypeExpr():
                        # intersection un interval avec un ensemble
                        return self.check_intersect_left(p_cand, p_expr)
            case AltTypeExpr():
                match p_expr:
                    case TypeVar():
                        # FIXME
                        # on coerce avec un type générique donc on "prends" le type de p_cand (TopDown)
                        return self.assoc_right(p_cand, p_expr)
                    case TypeNamed() | itvInt():
                        # intersection un ensemble et type nommé ou interval
                        return self.check_intersect_right(p_cand, p_expr)
                    case AltTypeExpr():
                        # intersection 2 ensembles
                        return self.check_intersect(p_cand, p_expr)
            case _:
                raise RuntimeError(f"Failed to match {type(p_cand)} to check_param")

    def check_expr(self, expr):
        match expr:
            case list():
                # first parameter collect candidates
                fname = self.get_fname(expr[0])
                fexpr = expr[1:]
                candidates = self._decls[fname].copy()
                alt = AltTypeExpr()
                for c in candidates:
                    # FIXME: rajouter des contextes pour le mapping des TypeVars
                    log.warning(f"Cand {c}")
                    # check last parameter of candidates as ellipsis
                    if len(c._types) < len(fexpr) and type(c._types[-1]) is not Ellipsis:
                        log.warning(f"Failed arity {c._types} / {fexpr}")
                        continue
                    coerce_fun = FunExpr(fname)
                    log.warning(f"LEN {len(c._types)} : {len(fexpr)}")
                    for p_cand, p_expr in zip(c._types, fexpr):
                        # coerce p_cand and p_expr
                        coerce_p = self.check_param(p_cand, p_expr)
                        if coerce_p is None:
                            continue
                        log.warning(f"PARAM {coerce_p}")
                        coerce_fun.add(coerce_p)
                    log.warning(f"ADD Cand {coerce_fun}")
                    alt.add(coerce_fun)
                return alt
            case _:
                raise RuntimeError(f"Failed to match {type(expr)} candidates to expression")

    def check(self):
        res = []
        # for each statements
        # FIXME: rajouter un contexte pour les intervals
        for stmt in self._stmts:
            res.append(self.check_expr(stmt))
            log.warning(f"LAST {res[-1]}")
        return res

__all__ = ['Val', 'Var', 'Fun', 'Def']
