from fuzzingbook.GrammarFuzzer import EvenFasterGrammarFuzzer
import grammar

class Fuzzer:
    def __init__(self):
        # This function must not be changed.
        self.grammar = grammar.grammar
        self.setup_fuzzer()
    
    def setup_fuzzer(self):
        # This function may be changed.
        self.fuzzer = EvenFasterGrammarFuzzer(self.grammar)

    def fuzz_one_input(self) -> str:
        # This function should be implemented, but the signature may not change.
        fuzzed_input = self.fuzzer.fuzz()
        print(fuzzed_input)
        return fuzzed_input