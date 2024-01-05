from fuzzingbook.GeneratorGrammarFuzzer import PGGCFuzzer
import grammar

class Fuzzer:
    def __init__(self):
        # This function must not be changed.
        self.grammar = grammar.grammar
        self.setup_fuzzer()
    
    def setup_fuzzer(self):
        # This function may be changed.
        self.fuzzer = PGGCFuzzer(self.grammar, min_nonterminals=0, max_nonterminals=100)

    def fuzz_one_input(self) -> str:
        # This function should be implemented, but the signature may not change.
        fuzzed_input = self.fuzzer.fuzz()
        return fuzzed_input