from itvArith.itv import *
from itertools import product
import logging

log = logging.getLogger(__name__)

class Val:
    """
    Value Declaration
    """
    def __init__(self, value, t=None):
        self._type = t
        self._value = value

    def __eq__(self, oth):
        if type(oth) is not Val:
            raise RuntimeError(f"Equality with another Val")
        return self._value == oth._value and self._type == oth._type

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

    def __eq__(self, oth):
        if type(oth) is not Var:
            raise RuntimeError(f"Equality with another Var")
        return self._name == oth._name and self._value == oth._value and self._type == oth._type

    def __repr__(self):
        return f"{self._name} = {self._value}:{self._type}"

class Param(Var):
    """
    Parameter declaration
    """
    def __init__(self, name=None, value=None, t=None):
        # si t null c'est qu'il est polymorphique
        if t is None:
            t = TypeVar()
        Var.__init__(self, name, value, t)

    def __eq__(self, oth):
        if type(oth) not in [Param, Var, Val]:
            raise RuntimeError(f"Equality with another Param, got {type(oth)}")
        match oth:
            case Val():
                return self._value == oth._value and self._type == oth._type
            case _:
                return self._name == oth._name and self._value == oth._value and self._type == oth._type

class Fun:
    """
    Function declaration

    suis la convention:
    NomFonction, TypeRetour, P1, P2, P3, ...
    """
    def __init__(self, name, *params):
        self._name = name
        #FIXME: rajouter le traitement des noms de paramètres et valeur par défaut
        # chaque élément du prototype doit être un Param
        for p in params:
            if type(p) is not Param:
                raise RuntimeError(f"Bad construction of Fun... arguments must be of type Param, found {type(p)}")
        self._params = params

    def __eq__(self, oth):
        if type(oth) is not Fun:
            raise RuntimeError(f"Equality with another Fun")
        for p1, p2 in zip(self._params, oth._params):
            if p1 != p2:
                return False
        return self._name == oth._name

    def __repr__(self):
        lr = [repr(it) for it in self._params[1:]]
        return f"fun {self._name}({', '.join(lr)}) -> {self._params[0]}"

class FunExpr:
    """
    Function call expression

    -Construit pendant le typage
    """
    def __init__(self, name, *args):
        self._name = name
        self._args = list(args)

    def __eq__(self, oth):
        if type(oth) is not FunExpr:
            raise RuntimeError(f"Equality with another FunExpr")
        for a1, a2 in zip(self._args, oth._args):
            if a1 != a2:
                return False
        return self._name == oth._name

    def add(self, arg):
        self._args.append(arg)

    @property
    def reftype(self):
        t = self._args[0]
        if hasattr(t, 'reftype'):
            return t.reftype
        return t

    def __repr__(self):
        lr = [repr(it) for it in self._args[1:]]
        txt = "()"
        if len(self._args):
            txt = f"({', '.join(lr)}) : {self._args[0]}"
        return f"{self._name}{txt}"

class AltTypeExpr:
    """
    Type alternatives

    -Collect et résoud les alternatives
    """
    def __init__(self):
        self._alts = []

    def add(self, alt):
        self._alts.append(alt)

    def insert(self, alts):
        self._alts += alts

    @property
    def is_typed(self):
        return len(self._alts) == 1

    @property
    def reftype(self):
        t = self._alts[0]
        if hasattr(t, 'reftype'):
            return t.reftype
        return t

    def __repr__(self):
        lr = [repr(it) for it in self._alts]
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
        #FIXME kw c'est les args de la definition de la fonction
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
                log.info(f"Def {v._name} in context {id(self._decls)}")
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
            return p_expr
        return None
        raise RuntimeError(f"Can't find CTOR {type(p_expr)} to {type(p_cand)}")

    def check_itv(self, p_cand, p_expr):
        """
        Coerce interval d'entier
        """
        # covariance des intervales
        if p_expr <= p_cand:
            return p_cand
        return None
        raise RuntimeError(f"Can't coerce {type(p_expr)} and {type(p_cand)}")

    def check_intersect_left(self, p_cand, p_expr):
        """
        Intersection de la gauche avec un ensemble de type à droite
        """
        return None
        raise RuntimeError(f"Can't coerce {type(p_expr)} and {type(p_cand)}")

    def check_intersect_right(self, p_cand, p_expr):
        """
        Intersection un ensemble de type à gauche et un type à droite
        """
        return None
        raise RuntimeError(f"Can't coerce {type(p_expr)} and {type(p_cand)}")

    def check_intersect(self, p_cand, p_expr):
        """
        Intersection 2 ensembles de type
        """
        alt = AltTypeExpr()
        log.info(f"INTERSECT {p_cand} and {p_expr}")
        for a1, a2 in product(p_cand._alts, p_expr._alts):
            coerce = self.check_param(a1, a2)
            if coerce is not None:
                alt.add(coerce)
        if len(alt._alts) == 0:
            return None
        return alt

    def check_param(self, p_cand, p_expr):
        log.warning(f"?? {type(p_cand)} // {type(p_expr)}")
        match (p_cand, p_expr):
            case (TypeVar(), _):
                # on coerce avec un type générique à gauche donc on "prends" le type de p_expr (BottomUp)
                return self.assoc_left(p_cand, p_expr)
            case (_, TypeVar()):
                # on coerce avec un type générique a droite donc on "prends" le type de p_cand (TopDown)
                return self.assoc_right(p_cand, p_expr)
            case (TypeNamed(), TypeNamed()):
                # check s'il existe une relation de covariance t1 > t2 ou un constructeur qu'on doit injecter
                return self.check_ctor(p_cand, p_expr)
            case (Param(), Var()):
                # check un paramètre de fonction avec une variable... les types doivents coercent
                return self.check_param(p_cand._type, p_expr._type)
            case (Param(), Val()):
                # check un paramètre de fonction avec une valeur... les types doivents coercent
                return self.check_param(p_cand._type, p_expr._type)
            case (itvInt(), itvInt()):
                # FIXME coerce interval Entier
                return self.check_itv(p_cand, p_expr)
            case (AltTypeExpr(), AltTypeExpr()):
                # intersection 2 ensembles
                return self.check_intersect(p_cand, p_expr)
            case (AltTypeExpr(), _):
                # intersection un ensemble et un type précis
                return self.check_intersect_right(p_cand, p_expr)
            case (_, AltTypeExpr()):
                # intersection un type précis avec un ensemble
                return self.check_intersect_left(p_cand, p_expr)
            case (_, _):
                return None
        raise RuntimeError(f"Failed to match {type(p_cand)} with {type(p_expr)}")

    def lookup(self, expr):
        alt = AltTypeExpr()
        log.info(f"LOOKUP {expr}")
        match expr:
            case str():
                if expr not in self._decls:
                    # ajoute la variable avec un TypeVar
                    # FIXME: TypeVar in context
                    self._decls[expr] = [Var(expr, None, TypeVar('T'))]
                # cherche la variable dans les paramètres ou contextes des déclarations
                alt.insert(self._decls[expr])
            case Val() | Var():
                # retourne le type de la valeur
                alt.add(expr)
            case AltTypeExpr():
                log.info(f"just AltTypeExpr")
                return expr
            case _:
                return None
                raise RuntimeError(f"Failed to lookup {type(expr)}")
        log.info(f"get {alt}")
        return alt

    def check_expr(self, expr):
        match expr:
            # une list représente l'appel d'une fonction
            case list():
                # le premier élément de la liste permet de collecter les candidats (overloadings)
                fname = self.get_fname(expr[0])
                # la suite de l'expression
                fexpr = expr[1:]
                # on fait une copie local pour altération
                candidates = self._decls[fname].copy()
                # l'objet alt va capturer toutes les alternatives
                alt = AltTypeExpr()
                for c in candidates:
                    class Next_candidates(Exception): pass
                    try:
                        # FIXME: rajouter des contextes pour le mapping des TypeVars
                        log.warning(f"Cand {c}")
                        # check last parameter of candidates as ellipsis
                        if len(c._params) < len(fexpr) and type(c._params[-1]) is not Ellipsis:
                            log.warning(f"Failed arity {c._params} / {fexpr}")
                            # abandonne ce candidat
                            continue
                        coerce_fun = FunExpr(fname)
                        log.warning(f"LEN {len(c._params)} : {len(fexpr)}")
                        # pour chaque argument de l'expression, on test le type du paramètre du candidat
                        for p_cand, p_expr in zip(c._params, fexpr):
                            p_cand = self.lookup(p_cand)
                            p_expr = self.lookup(p_expr)
                            log.warning(f"Try coerce {p_cand} with {p_expr}")
                            # coercion entre p_cand et p_expr
                            coerce_p = self.check_param(p_cand, p_expr)
                            log.error(f"COERCE {coerce_p}")
                            if coerce_p is None:
                                # abandonne ce candidat
                                log.warning(f"NEXT CANDIDATE")
                                raise Next_candidates
                            log.warning(f"PARAM {coerce_p}")
                            coerce_fun.add(coerce_p)
                        log.warning(f"ADD Cand {coerce_fun}")
                        alt.add(coerce_fun)
                    except Next_candidates:
                        continue
                return alt
            case _:
                return None
                raise RuntimeError(f"Failed to match {type(expr)} candidates to expression")

    def check(self):
        res = []
        # for each statements
        # FIXME: rajouter un contexte pour les copies locals lors du flow sensitive type checking
        for stmt in self._stmts:
            res.append(self.check_expr(stmt))
            log.warning(f"LAST {res[-1]}")
        return res

__all__ = ['Val', 'Var', 'Fun', 'Def', 'AltTypeExpr', 'FunExpr', 'Param']
