class GreyNumber:
    def __init__(self, low, up):
        self.low = low
        self.up = up

def probability_greater(a: GreyNumber, b: GreyNumber) -> float:
    low_a, up_a = a.low, a.up
    low_b, up_b = b.low, b.up

    if low_a > up_b:
        return 1
    elif low_b > up_a:
        return 0
    elif low_a == low_b or up_a == up_b:
        raise ValueError("Lower or upper bounds of compared grey numbers are equal; this case is not supported for comparison.")
    elif low_a < low_b < up_a < up_b:
        return (up_a - low_b) ** 2 / (2 * (up_a - low_a) * (up_b - low_b))
    elif low_b < low_a < up_b < up_a:
        return 1 - (up_b - low_a) ** 2 / (2 * (up_a - low_a) * (up_b - low_b))
    elif low_b < low_a < up_a < up_b:
        return (low_a + up_a - 2 * low_b) / (2 * (up_b - low_b))
    elif low_a < low_b < up_b < up_a:
        return (2 * up_a - up_b - low_b) / (2 * (up_a - low_a))
    else:
        raise ValueError("Sorry, this case is not supported")

class GreyNumberBatchComparator:
    def __init__(self, grey_numbers):
        self.numbers = [GreyNumber(low, up) for low, up in self.adjust_equal_bounds(grey_numbers)]

    def adjust_equal_bounds(self, grey_numbers):
        epsilon = 1e-7
        n = len(grey_numbers)
        lows = [low for low, up in grey_numbers]
        ups = [up for low, up in grey_numbers]

        combined = []
        for i in range(n):
            combined.append((lows[i], i, 'low'))
            combined.append((ups[i], i, 'up'))

        combined.sort(key=lambda x: x[0])

        for i in range(1, len(combined)):
            prev_val, prev_idx, prev_type = combined[i-1]
            cur_val, cur_idx, cur_type = combined[i]
            if cur_val <= prev_val + 1e-12:
                combined[i] = (prev_val + epsilon, cur_idx, cur_type)

        for val, idx, t in combined:
            if t == 'low':
                lows[idx] = val
            else:
                ups[idx] = val

        return list(zip(lows, ups))

    def probability_greater(self, a, b):
        return probability_greater(a, b)

    def compare_all_pairs(self):
        results = []
        n = len(self.numbers)
        for i in range(n):
            for j in range(i + 1, n):
                try:
                    prob = self.probability_greater(self.numbers[i], self.numbers[j])
                    results.append(f"Possibility (X{i+1} > X{j+1}) = {prob:.7f}")
                except ValueError as e:
                    results.append(f"Error comparing X{i+1} and X{j+1}: {str(e)}")
        return "\n".join(results)


class MinimaxRegretApproach:
    def __init__(self, grey_numbers):
        self.numbers = [{"low": low, "up": up} for low, up in grey_numbers]
        self.n = len(self.numbers)
        self.ranks = [0] * self.n

    def compute_max_regret(self, current_indices):
        max_regrets = []
        for i in current_indices:
            low_i = self.numbers[i]["low"]
            up_i = self.numbers[i]["up"]
            regrets = []
            for j in current_indices:
                if i == j:
                    continue
                low_j = self.numbers[j]["low"]
                up_j = self.numbers[j]["up"]
                regret = max(0, up_j - low_i)
                regrets.append(regret)
            max_regrets.append((i, max(regrets) if regrets else 0))
        return max_regrets

    def rank_numbers(self):
        remaining = list(range(self.n))
        current_rank = self.n

        while remaining:
            max_regrets = self.compute_max_regret(remaining)
            min_regret_value = min(x[1] for x in max_regrets)
            candidates = [x[0] for x in max_regrets if x[1] == min_regret_value]
            chosen = candidates[0]

            self.ranks[chosen] = current_rank
            current_rank -= 1
            remaining.remove(chosen)

        sorted_indices = sorted(range(self.n), key=lambda i: self.ranks[i], reverse=True)
        return sorted_indices, self.ranks

class DiscreteGreyNumberComparator:
    """
    Placeholder for Discrete Grey Number comparison.
    Later, this class will implement comparison logic
    according to the discrete grey number algorithm
    you’ll provide.
    """
    def __init__(self, grey_numbers):
        # grey_numbers expected as list of tuples or discrete sets
        self.grey_numbers = grey_numbers

    def compare(self):
        # Temporary placeholder
        return "Discrete Grey Number comparison will be implemented soon."

# ================================
# Discrete Grey Numbers Comparator
# ================================
from collections import Counter
from typing import List, Tuple, Dict

class DiscreteGreyNumberComparator:
    """
    Compare two discrete grey numbers ⊗a and ⊗b.

    Inputs are two lists of values (possibly with duplicates) and optional
    per-occurrence probabilities. If probabilities are provided per occurrence,
    duplicates are aggregated by summing their probabilities. If probabilities
    are omitted, use relative frequencies of distinct values.

    Output:
      - P_ab = p(⊗a > ⊗b)
      - P_ba = p(⊗b > ⊗a)
      - P_eq = p(⊗a = ⊗b)
      - p_adv(a) = P_ab + 0.5*P_eq
      - p_adv(b) = P_ba + 0.5*P_eq
      - detailed log (step-by-step text)
    """

    @staticmethod
    def _parse_list_of_floats(csv: str) -> List[float]:
        parts = [s.strip() for s in csv.split(",") if s.strip() != ""]
        return [float(x) for x in parts]

    @staticmethod
    def _build_probabilities(values_csv: str, probs_csv: str = "") -> Tuple[Dict[float, float], str]:
        """
        Returns (prob_dict, pretty_table_text).
        prob_dict maps distinct value -> probability, with sum == 1 (normalized if needed).
        If probs_csv == "" -> derive from relative frequency of distinct values.
        Else probs_csv must have same length as values list; duplicates get aggregated.
        """
        vals = DiscreteGreyNumberComparator._parse_list_of_floats(values_csv)
        if not vals:
            raise ValueError("Values list cannot be empty.")
        N = len(vals)

        table_lines = []
        if probs_csv.strip() == "":
            # derive from multiplicity (relative frequency of distinct values)
            cnt = Counter(vals)
            total = float(N)
            prob = {v: cnt[v] / total for v in sorted(cnt.keys())}
            table_lines.append("  • probabilities inferred from multiplicity:")
            table_lines.append("    value\tcount\tp")
            for v in sorted(cnt.keys()):
                table_lines.append(f"    {v}\t{cnt[v]}\t{prob[v]:.6f}")
            return prob, "\n".join(table_lines)

        # user provided per-occurrence probabilities
        prs = DiscreteGreyNumberComparator._parse_list_of_floats(probs_csv)
        if len(prs) != N:
            raise ValueError("Length of probabilities must match number of values.")
        # aggregate duplicates by value
        agg: Dict[float, float] = {}
        for v, p in zip(vals, prs):
            agg[v] = agg.get(v, 0.0) + p

        # normalize softly to 1 (tolerance for rounding)
        s = sum(agg.values())
        if s <= 0:
            raise ValueError("Sum of probabilities must be positive.")
        for k in agg:
            agg[k] /= s

        table_lines.append("  • probabilities taken from user input (duplicates aggregated):")
        table_lines.append("    value\tp (normalized)")
        for v in sorted(agg.keys()):
            table_lines.append(f"    {v}\t{agg[v]:.6f}")
        return agg, "\n".join(table_lines)

    @staticmethod
    def compare(a_values_csv: str, a_probs_csv: str,
                b_values_csv: str, b_probs_csv: str) -> Tuple[float, float, float, float, float, str]:
        """
        Core comparison per discrete grey numbers:
          P_ab = Σ_i Σ_j I(a_i > b_j) p_ai p_bj
          P_ba = Σ_i Σ_j I(b_j > a_i) p_ai p_bj
          P_eq = Σ_i Σ_j I(a_i = b_j) p_ai p_bj
        Returns (P_ab, P_ba, P_eq, p_adv_a, p_adv_b, log_text)
        """
        a_prob, a_txt = DiscreteGreyNumberComparator._build_probabilities(a_values_csv, a_probs_csv)
        b_prob, b_txt = DiscreteGreyNumberComparator._build_probabilities(b_values_csv, b_probs_csv)

        # Cross pairs
        pairs_lines = ["\nPairwise contributions (distinct-by-distinct):",
                       "  a_value\tb_value\trelation\tp_ai*p_bj\tadds_to"]
        P_ab = P_ba = P_eq = 0.0
        for av in sorted(a_prob.keys()):
            for bv in sorted(b_prob.keys()):
                w = a_prob[av] * b_prob[bv]
                if av > bv:
                    P_ab += w
                    pairs_lines.append(f"  {av}\t{bv}\t>\t{w:.6f}\tP(a>b)")
                elif av < bv:
                    P_ba += w
                    pairs_lines.append(f"  {av}\t{bv}\t<\t{w:.6f}\tP(b>a)")
                else:
                    P_eq += w
                    pairs_lines.append(f"  {av}\t{bv}\t=\t{w:.6f}\tP(a=b)")

        p_adv_a = P_ab + 0.5 * P_eq
        p_adv_b = P_ba + 0.5 * P_eq
    # --------- NEW: reusable pairwise on prob dicts ---------
    @staticmethod
    def _pairwise_from_probs(a_prob: Dict[float, float], b_prob: Dict[float, float]):
        """
        Compute P(a>b), P(b>a), P(a=b) given two {value->p} dicts.
        """
        P_ab = P_ba = P_eq = 0.0
        for av, pa in a_prob.items():
            for bv, pb in b_prob.items():
                w = pa * pb
                if av > bv:
                    P_ab += w
                elif av < bv:
                    P_ba += w
                else:
                    P_eq += w
        return P_ab, P_ba, P_eq

    # --------- NEW: compare many sets at once ---------
    @staticmethod
    def compare_many(items: List[Tuple[str, str, str]]):
        """
        items: list of (label, values_csv, probs_csv)
        Returns:
          labels: List[str]
          M_gt:   NxN matrix where M_gt[i][j] = P(S_i > S_j)
          M_eq:   NxN matrix where M_eq[i][j] = P(S_i = S_j)
          M_adv:  NxN matrix where M_adv[i][j] = P(S_i > S_j) + 0.5*P(S_i = S_j)
          scores: length-N list where scores[i] = sum_{j!=i} M_adv[i][j]
          order:  indices sorted by scores desc (largest to smallest)
          log:    detailed text report
        """
        if len(items) < 2:
            raise ValueError("Need at least two discrete grey numbers to compare.")

        # 1) Build per-set probability dicts (using existing builder)
        labels = []
        probs  = []      # list[Dict[value->p]]
        parts_log = []   # per-set logs (frequency table or normalized p)
        for (lbl, vcsv, pcsv) in items:
            p_dict, txt = DiscreteGreyNumberComparator._build_probabilities(vcsv, pcsv)
            labels.append(lbl or f"Set{len(labels)+1}")
            probs.append(p_dict)
            parts_log.append((labels[-1], txt))

        n = len(labels)
        # 2) Build pairwise matrices
        M_gt = [[0.0]*n for _ in range(n)]
        M_eq = [[0.0]*n for _ in range(n)]
        M_adv = [[0.0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                P_ab, P_ba, P_eq = DiscreteGreyNumberComparator._pairwise_from_probs(probs[i], probs[j])
                # here "ab" means i over j
                M_gt[i][j] = P_ab
                M_eq[i][j] = P_eq
                M_adv[i][j] = P_ab + 0.5*P_eq

        # 3) Aggregate scores per set (tournament-style)
        scores = []
        for i in range(n):
            s = sum(M_adv[i][j] for j in range(n) if j != i)
            scores.append(s)

        order = sorted(range(n), key=lambda k: (-scores[k], labels[k]))

        # 4) Log text
        def fmt_row(row): return "  ".join(f"{x:0.6f}" for x in row)
        log_lines = []
        log_lines.append("Discrete Grey Numbers — Multi-set comparison (pairwise & ranking)")
        log_lines.append("\nPer-set probability tables:")
        for (lbl, txt) in parts_log:
            log_lines.append(f"\n[{lbl}]")
            log_lines.append(txt)

        log_lines.append("\nMatrix M_gt[i][j] = P(S_i > S_j):")
        log_lines.append("      " + "  ".join(f"{labels[j]:>8}" for j in range(n)))
        for i in range(n):
            log_lines.append(f"{labels[i]:>6}  {fmt_row(M_gt[i])}")

        log_lines.append("\nMatrix M_eq[i][j] = P(S_i = S_j):")
        log_lines.append("      " + "  ".join(f"{labels[j]:>8}" for j in range(n)))
        for i in range(n):
            log_lines.append(f"{labels[i]:>6}  {fmt_row(M_eq[i])}")

        log_lines.append("\nAdvantage matrix M_adv[i][j] = P(>) + 0.5 P(=):")
        log_lines.append("      " + "  ".join(f"{labels[j]:>8}" for j in range(n)))
        for i in range(n):
            log_lines.append(f"{labels[i]:>6}  {fmt_row(M_adv[i])}")

        log_lines.append("\nScores (sum of row i, j≠i, from M_adv):")
        for i in range(n):
            log_lines.append(f"  {labels[i]}: {scores[i]:0.6f}")

        log_lines.append("\nRanking (largest → smallest):")
        for rank, idx in enumerate(order, 1):
            log_lines.append(f"  {rank}. {labels[idx]}  (score={scores[idx]:0.6f})")

        return labels, M_gt, M_eq, M_adv, scores, order, "\n".join(log_lines)

        # Build full log
        log = []
        log.append("Discrete Grey Numbers — Step-by-step")
        log.append("\nSet ⊗a:")
        log.append(a_txt)
        log.append("\nSet ⊗b:")
        log.append(b_txt)
        log.extend(pairs_lines)
        log.append("\nTotals:")
        log.append(f"  P(a>b) = {P_ab:.6f}")
        log.append(f"  P(b>a) = {P_ba:.6f}")
        log.append(f"  P(a=b) = {P_eq:.6f}")
        log.append(f"\nAdvantage probabilities:")
        log.append(f"  p_adv(a) = P(a>b) + 0.5*P(a=b) = {p_adv_a:.6f}")
        log.append(f"  p_adv(b) = P(b>a) + 0.5*P(a=b) = {p_adv_b:.6f}")
        if p_adv_a > p_adv_b:
            log.append(f"\nDecision: ⊗a >_{p_adv_a:.6f} ⊗b")
        elif p_adv_b > p_adv_a:
            log.append(f"\nDecision: ⊗b >_{p_adv_b:.6f} ⊗a")
        else:
            log.append("\nDecision: ⊗a and ⊗b are indifferent under this rule.")
        return P_ab, P_ba, P_eq, p_adv_a, p_adv_b, "\n".join(log)

