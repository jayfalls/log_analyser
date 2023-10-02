from collections import Counter
import spacy
from spacy.tokens import Doc
from typing import List, Tuple


class LogTokeniser():
    filters: tuple
    infrequent_threshold: int = 2 # The minimum number of occurrences required for a token to be considered significant
    
    @staticmethod
    def tokenise_log_message(log_message: str) -> Doc:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(log_message)
        return doc
    
    def tokenise_log_messages(self, log_messages: tuple) -> List[str]:
        
        tokenised_messages: List[Doc] = []
        for log_message in log_messages:
            tokenised_messages.append(self.tokenise_log_message(log_message))
        tokens = [token.token for doc in tokenised_messages for token in doc]
        return tokens

    @staticmethod
    def get_token_frequencies(tokens: List[str]):
        token_frequencies = Counter(tokens)
        return token_frequencies

    @staticmethod
    # Sorts the tokens in descending order
    def sort_token_frequencies(token_frequencies: List[Tuple[str, int]]) -> dict:
        sorted_frequencies: List[Tuple[str, int]] = sorted(token_frequencies, key=lambda x: x[1], reverse=True)
        return sorted_frequencies
    
    # Filters out infrequent occurences
    def filter_token_frequencies(self, token_frequencies: List[Tuple[str, int]]) -> List[Tuple[str, int]]:
        filtered_token_frequencies: List[Tuple[str, int]] = [token_freq for token_freq in token_frequencies if token_freq[1] >= self.infrequent_threshold]
        return filtered_token_frequencies
    
    @staticmethod
    def find_recurring_patterns(filtered_token_frequencies: List[Tuple[str, int]]) -> List[str]:
        patterns: List[str] = []
        for token, frequency in filtered_token_frequencies:
            if len(token.split()) > 1:
                patterns.append(token)
            else:
                for pattern in patterns:
                    if pattern in token:
                        patterns.append(token)
                        break
        return patterns
    
    @staticmethod
    def print_recurring_patterns(recurring_patterns: List[str]) -> None:
        if not recurring_patterns:
            print("No recurring patterns found.")
        else:
            print("Recurring patterns:")
            nlp = spacy.load("en_core_web_sm")
            for pattern in recurring_patterns:
                doc = nlp(pattern)
                untokenised_pattern = " ".join([token.text for token in doc])
                print("- " + untokenised_pattern)

    def get_frequent_logs_tokenised(self, log_analyser) -> None:
        logs: tuple = log_analyser.get_logs(self.filters)
        tokenised_messages: List[str] = self.tokenise_log_messages(logs)
        frequencies = self.get_token_frequencies(tokenised_messages)
        print(frequencies)
        sorted_frequencies = self.sort_token_frequencies(frequencies)
        filtered_frequencies = self.filter_token_frequencies(sorted_frequencies)
        print(filtered_frequencies)
        patterns: List[str] = self.find_recurring_patterns(filtered_token_frequencies)
        self.print_recurring_patterns(patterns)

    