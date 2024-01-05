from fuzzingbook.GeneratorGrammarFuzzer import PGGCFuzzer, DerivationTree, Expansion, Dict, List, Union, Set
from fuzzingbook.Grammars import Grammar
import grammar
import copy

class FasterPGGCFuzzer(PGGCFuzzer):
    def __init__(self, grammar: Grammar, *, replacement_attempts: int = 10, **kwargs) -> None:
        super().__init__(grammar, replacement_attempts=replacement_attempts, **kwargs)
        self._expansion_cache: Dict[Expansion, List[DerivationTree]] = {}
        self._expansion_invocations = 0
        self._expansion_invocations_cached = 0

    def expansion_to_children(self, expansion: Expansion) \
            -> List[DerivationTree]:
        self._expansion_invocations += 1

        expansion_str = expansion
        if type(expansion_str) == tuple:
            expansion_str = expansion_str[0]

        if expansion_str in self._expansion_cache:
            self._expansion_invocations_cached += 1
            cached_result = copy.deepcopy(self._expansion_cache[expansion_str])
            return cached_result


        result = super().expansion_to_children(expansion)
        self._expansion_cache[expansion_str] = copy.deepcopy(result)
        return result

class EvenFasterPGGCFuzzer(PGGCFuzzer):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._symbol_costs: Dict[str, Union[int, float]] = {}
        self._expansion_costs: Dict[Expansion, Union[int, float]] = {}
        self.precompute_costs()
    
    def new_symbol_cost(self, symbol: str,
                        seen: Set[str] = set()) -> Union[int, float]:
        return self._symbol_costs[symbol]

    def new_expansion_cost(self, expansion: Expansion,
                           seen: Set[str] = set()) -> Union[int, float]:
        expansion_str = expansion
        if type(expansion_str) == tuple:
            expansion_str = expansion_str[0]
        return self._expansion_costs[expansion_str]

    def precompute_costs(self) -> None:
        for symbol in self.grammar:
            self._symbol_costs[symbol] = super().symbol_cost(symbol)
            for expansion in self.grammar[symbol]:
                expansion_str = expansion
                if type(expansion_str) == tuple:
                    expansion_str = expansion_str[0]
                self._expansion_costs[expansion_str] = \
                    super().expansion_cost(expansion)

        # Make sure we now call the caching methods
        self.symbol_cost = self.new_symbol_cost  # type: ignore
        self.expansion_cost = self.new_expansion_cost  # type: ignore

class Fuzzer:
    def __init__(self):
        # This function must not be changed.
        self.grammar = grammar.grammar
        self.setup_fuzzer()
    
    def setup_fuzzer(self):
        # This function may be changed.
        # self.fuzzer = PGGCFuzzer(self.grammar)
        # self.fuzzer = FasterPGGCFuzzer(self.grammar)
        self.fuzzer = EvenFasterPGGCFuzzer(self.grammar, min_nonterminals=0, max_nonterminals=100)

    def fuzz_one_input(self) -> str:
        # This function should be implemented, but the signature may not change.
        fuzzed_input = self.fuzzer.fuzz()
        return fuzzed_input