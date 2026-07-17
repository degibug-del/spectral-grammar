#!/usr/bin/env python3
"""
Build large training corpus from multiple sources.

Sources:
1. NLTK sentence corpus (1,600+ sentences)
2. Generated variations on grammar patterns
3. Manually curated complex structures
4. Synthetic ambiguities
"""

import random


def get_nltk_sentences():
    """Get sentences from NLTK corpus."""
    try:
        import nltk
        from nltk.corpus import sentence_polarity, brown

        # Try to use existing NLTK data
        try:
            sentences = list(sentence_polarity.sents())
            sentences = [' '.join(s) + '.' for s in sentences]
            print(f"  Loaded {len(sentences)} from sentence_polarity")
            return sentences
        except:
            pass
    except:
        pass

    return []


def get_grammar_patterns():
    """Generate diverse grammatical structures."""
    subjects = [
        "The cat", "The dog", "The bird", "The horse", "The rabbit",
        "John", "Mary", "Sarah", "Tom", "Alice",
        "The teacher", "The student", "The professor", "The doctor",
        "The company", "The government", "The organization",
        "Technology", "Science", "Art", "Music", "Nature",
    ]

    verbs = [
        "sat on", "ran to", "walked in", "jumped over", "flew past",
        "gave to", "showed", "told", "asked", "explained",
        "discovered", "created", "built", "destroyed", "changed",
        "studied", "learned", "taught", "read", "wrote",
    ]

    objects = [
        "the mat", "the park", "the door", "the fence", "the tree",
        "the book", "the letter", "the package", "the gift", "the key",
        "a theory", "a problem", "a solution", "an idea", "a concept",
        "his friend", "her brother", "the team", "the project",
    ]

    modifiers = [
        "",  # No modifier
        "quickly",
        "slowly",
        "carefully",
        "yesterday",
        "today",
        "tomorrow",
        "in the morning",
        "at night",
        "while walking",
        "after dinner",
        "because he was tired",
    ]

    sentences = []
    for subj in subjects[:10]:
        for verb in verbs[:10]:
            for obj in objects[:10]:
                for mod in modifiers[:5]:
                    if mod:
                        sent = f"{subj} {verb} {obj} {mod}."
                    else:
                        sent = f"{subj} {verb} {obj}."
                    sentences.append(sent)

    return sentences


def get_complex_structures():
    """Manually curated complex and ambiguous sentences."""
    return [
        # Garden-path sentences
        "The horse raced past the barn fell.",
        "The old man the boat.",
        "The complex houses married and single people.",
        "The trophy doesn't fit in the suitcase because it is too large.",
        "The trophy doesn't fit in the suitcase because it is too small.",

        # Attachment ambiguities
        "I shot the elephant in my pajamas.",
        "She saw the man on the hill with a telescope.",
        "The president criticized the report in the meeting.",

        # Center embedding
        "The book that the student read was interesting.",
        "The book that the student that enrolled in my class read was interesting.",
        "The girl that the boy that the dog chased saw was crying.",

        # Relative clauses
        "The researcher who the professor knew discovered the solution.",
        "The student who everyone thought was brilliant failed the exam.",
        "The idea that the committee discussed seemed promising.",

        # Extraposition
        "It is clear that the theory is wrong.",
        "It is obvious that she will succeed.",
        "It seems that everyone agrees.",

        # Coordination
        "John and Mary went to the store.",
        "John went to the store and Mary went to the park.",
        "John bought a book, Mary bought a pen, and Sarah bought a notebook.",

        # Negation
        "I don't think he is coming.",
        "Nobody saw nothing.",
        "It is not the case that he is happy.",

        # Cleft
        "It was Mary who called.",
        "It is the grammar that is difficult.",
        "What I like is ice cream.",

        # Passive
        "The book was written by the author.",
        "The email was sent by the assistant yesterday.",
        "The solution was found by the team working together.",

        # Questions
        "What did she buy?",
        "Who did the teacher help?",
        "Where did they go after school?",
        "Why is the sky blue?",

        # Comparatives
        "The car is faster than the bicycle.",
        "John is as tall as Mary.",
        "She runs faster than anyone else in the class.",

        # Conditionals
        "If the weather is nice, we will go outside.",
        "Unless you study hard, you won't pass the exam.",
        "Should you need help, please call me.",

        # Infinitives
        "I want to read the book.",
        "She asked him to leave.",
        "The book is easy to read.",
        "To understand this theory is difficult.",

        # Gerunds
        "Running is good exercise.",
        "She enjoys reading books.",
        "Solving this problem requires patience.",

        # Participles
        "Running down the street, he saw his friend.",
        "Shocked by the news, she didn't know what to say.",
        "The book lying on the table is mine.",

        # Appositives
        "John, my best friend, is coming tomorrow.",
        "The capital of France, Paris, is a beautiful city.",

        # Parentheticals
        "The solution, I believe, is obvious.",
        "She will, no doubt, succeed.",

        # Multiple embeddings
        "The fact that the theory that he proposed was wrong surprised everyone.",
        "The idea that the solution that the team found was effective seemed clear.",
    ]


def get_synthetic_variations():
    """Generate synthetic variations of core patterns."""
    base_structures = [
        ("Simple SVO", "{subject} {verb} {object}.", ["The cat sat on the mat"]),
        ("With adverb", "{subject} {adverb} {verb} {object}.", ["The cat quickly sat on the mat"]),
        ("With adjective", "The {adjective} {noun} {verb} {object}.", ["The black cat sat on the mat"]),
        ("Embedded clause", "{subject} {verb} that {clause}.", ["The teacher said that the student was late"]),
        ("Relative clause", "{subject} that {clause} {verb}.", ["The book that I read yesterday was good"]),
    ]

    subjects = ["The cat", "A bird", "The teacher", "My friend"]
    verbs = ["sat", "ran", "jumped", "walked"]
    objects = ["on the mat", "in the park", "over the fence", "through the door"]
    adverbs = ["quickly", "slowly", "carefully", "happily"]
    adjectives = ["black", "big", "small", "old", "new"]
    nouns = ["cat", "bird", "dog", "horse", "rabbit"]

    sentences = []
    for subj in subjects:
        for verb in verbs:
            for obj in objects:
                sentences.append(f"{subj} {verb} {obj}.")

    for adj in adjectives:
        for noun in nouns:
            for verb in verbs:
                for obj in objects:
                    sentences.append(f"The {adj} {noun} {verb} {obj}.")

    return sentences


def clean_sentence(sent):
    """Clean and normalize sentence."""
    sent = sent.strip()
    if not sent:
        return None

    # Ensure proper punctuation
    if not sent.endswith(('.', '!', '?')):
        sent = sent + '.'

    # Remove extra whitespace
    sent = ' '.join(sent.split())

    # Skip if too short or too long
    words = sent.split()
    if len(words) < 2 or len(words) > 50:
        return None

    return sent


def main():
    print("=" * 80)
    print("BUILDING LARGE TRAINING CORPUS")
    print("=" * 80)
    print()

    all_sentences = set()  # Use set to avoid duplicates

    # Source 1: NLTK
    print("1. Fetching NLTK corpus...")
    nltk_sents = get_nltk_sentences()
    print(f"   Got {len(nltk_sents)} sentences")
    all_sentences.update(nltk_sents)

    # Source 2: Grammar patterns (systematic generation)
    print("2. Generating grammar patterns...")
    grammar_sents = get_grammar_patterns()
    print(f"   Generated {len(grammar_sents)} sentences")
    all_sentences.update(grammar_sents)

    # Source 3: Complex structures (hand-curated)
    print("3. Adding complex structures...")
    complex_sents = get_complex_structures()
    print(f"   Added {len(complex_sents)} sentences")
    all_sentences.update(complex_sents)

    # Source 4: Synthetic variations
    print("4. Generating synthetic variations...")
    synthetic_sents = get_synthetic_variations()
    print(f"   Generated {len(synthetic_sents)} sentences")
    all_sentences.update(synthetic_sents)

    # Clean sentences
    print("\n5. Cleaning corpus...")
    cleaned = []
    for sent in all_sentences:
        clean = clean_sentence(sent)
        if clean:
            cleaned.append(clean)

    # Remove duplicates (case-insensitive)
    normalized = {}
    for sent in cleaned:
        key = sent.lower()
        if key not in normalized:
            normalized[key] = sent

    final_corpus = list(normalized.values())
    random.shuffle(final_corpus)

    print(f"\nFinal corpus statistics:")
    print(f"  Total sentences: {len(final_corpus)}")
    print(f"  Min words: {min(len(s.split()) for s in final_corpus)}")
    print(f"  Max words: {max(len(s.split()) for s in final_corpus)}")
    print(f"  Avg words: {sum(len(s.split()) for s in final_corpus) / len(final_corpus):.1f}")

    # Save corpus
    corpus_file = "corpus_large.txt"
    with open(corpus_file, "w") as f:
        for sent in final_corpus:
            f.write(sent + "\n")

    print(f"\n✓ Corpus saved to: {corpus_file}")
    print()

    # Show sample
    print("Sample sentences from corpus:")
    for sent in final_corpus[:10]:
        print(f"  - {sent}")


if __name__ == "__main__":
    main()
