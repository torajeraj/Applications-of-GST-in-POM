import numpy as np

class DengIncidence:
    def __init__(self):
        self.difference_max = 0
        self.difference_min = float('inf')

    def getInitialImage(self, data):
        rows, cols = len(data), len(data[0])
        return [[data[i][j] / data[i][0] for j in range(cols)] for i in range(rows)]

    def getDifferenceArray(self, array):
        rows, cols = len(array), len(array[0])
        diff_array = []
        self.difference_max = 0
        self.difference_min = float('inf')
        for i in range(1, rows):
            row = []
            for j in range(cols):
                diff = abs(array[0][j] - array[i][j])
                row.append(diff)
                if diff > self.difference_max:
                    self.difference_max = diff
                if diff < self.difference_min:
                    self.difference_min = diff
            diff_array.append(row)
        return diff_array

    def getIncidenceCoeff(self, coef, maxD, minD, diffArray):
        rows, cols = len(diffArray), len(diffArray[0])
        coeffs = []
        for i in range(rows):
            row = []
            for j in range(cols):
                if maxD == minD:
                    val = 1.0
                else:
                    val = (minD + coef * maxD) / (diffArray[i][j] + coef * maxD)
                row.append(val)
            coeffs.append(row)
        return coeffs

    def getIncidenceDegree(self, coeffs):
        return [sum(row) / len(row) for row in coeffs]

    def compute_all_steps(self, seq1, seq2, coef, precision=4):
        data = [seq1, seq2]
        initial = self.getInitialImage(data)
        difference = self.getDifferenceArray(initial)
        max_diff = self.difference_max
        min_diff = self.difference_min
        coeffs = self.getIncidenceCoeff(coef, max_diff, min_diff, difference)
        degrees = self.getIncidenceDegree(coeffs)

        def format_matrix(mat):
            return "\n".join(
                ["  ".join(f"{elem:.{precision}f}" for elem in row) for row in mat]
            )

        steps_text = (
            "Step 1: Initial Image:\n" + format_matrix(initial) + "\n\n"
            + "Step 2: Difference Array:\n" + format_matrix(difference) + "\n\n"
            + f"Step 3: Max difference = {max_diff:.{precision}f}\n\n"
            + f"Step 4: Min difference = {min_diff:.{precision}f}\n\n"
            + "Step 5: Incidence Coefficients:\n" + format_matrix(coeffs) + "\n\n"
            + "Step 6: Degree of Incidence:\n"
            + "\n".join(f"{deg:.{precision}f}" for deg in degrees) + "\n"
        )
        return steps_text, degrees


class AbsoluteIncidence:
    def __init__(self, data, precision):
        self.data = data
        self.precision = precision

    def getInitExcelDataArray(self, row):
        return self.data[row]

    def getFirstPointZero(self, arr):
        base = arr[0]
        return [round(x - base, self.precision) for x in arr]

    def computeSnum(self, arr):
        s = sum(arr[1:-1]) + arr[-1] / 2.0
        return abs(s)

    def computeSi_S0(self, arr1, arr2):
        s = 0
        for i in range(1, len(arr1) - 1):
            s += arr2[i] - arr1[i]
        s += (arr2[-1] - arr1[-1]) / 2.0
        return abs(s)

    def calculate(self):
        results = []
        n = len(self.data)
        num = 0
        for i in range(n):
            for j in range(i + 1, n):
                num += 1
                arr1 = self.getInitExcelDataArray(i)
                arr2 = self.getInitExcelDataArray(j)
                point_zero1 = self.getFirstPointZero(arr1)
                point_zero2 = self.getFirstPointZero(arr2)
                num2 = self.computeSnum(point_zero1)
                num3 = self.computeSnum(point_zero2)
                num4 = self.computeSi_S0(point_zero1, point_zero2)
                degree = (1.0 + num2 + num3) / (1.0 + num2 + num3 + num4)
                results.append(f"{num}: Calculation of absolute degree of incidence for Sequence between [{i + 1}] and [{j + 1}]\n\n")
                results.append(f"(1) Starting point zeroing of sequences:\n Sequence[{i + 1}]: {point_zero1}\n Sequence[{j + 1}]: {point_zero2}\n\n")
                results.append(f"(2) Compute |s0|={num2};  |s1|={num3};  |s1-s0|={num4}\n\n")
                results.append(f"(3) Compute absolute degree of grey incidence between Sequence [{i + 1}] and Sequence [{j + 1}]:\n")
                results.append(f"    Sequence({i + 1}{j + 1}) = {degree:.4f}\n\n")
        return "".join(results)


class RelativeIncidence:
    def getInitialValueImage(self, excelArray):
        length = len(excelArray)
        length2 = len(excelArray[0])
        array = [[0]*length2 for _ in range(length)]
        for i in range(length):
            base = excelArray[i][0]
            for j in range(length2):
                array[i][j] = excelArray[i][j] / base
        return array


class SynthesisIncidence:
    def __init__(self, data, precision, weight):
        self.data = data
        self.precision = precision
        self.weight = weight

    def calculate(self):
        relative = RelativeIncidence()
        relative_data = relative.getInitialValueImage(self.data)
        absolute = AbsoluteIncidence(self.data, self.precision)
        absolute_relative = AbsoluteIncidence(relative_data, self.precision)
        results = []
        n = len(self.data)
        num = 0
        for i in range(n):
            for j in range(i + 1, n):
                num += 1
                arr1_abs = absolute.getInitExcelDataArray(i)
                arr2_abs = absolute.getInitExcelDataArray(j)
                fz1_abs = absolute.getFirstPointZero(arr1_abs)
                fz2_abs = absolute.getFirstPointZero(arr2_abs)
                sn1_abs = absolute.computeSnum(fz1_abs)
                sn2_abs = absolute.computeSnum(fz2_abs)
                sis0_abs = absolute.computeSi_S0(fz1_abs, fz2_abs)
                abs_degree = (1.0 + sn1_abs + sn2_abs) / (1.0 + sn1_abs + sn2_abs + sis0_abs)
                arr1_rel = absolute_relative.getInitExcelDataArray(i)
                arr2_rel = absolute_relative.getInitExcelDataArray(j)
                fz1_rel = absolute_relative.getFirstPointZero(arr1_rel)
                fz2_rel = absolute_relative.getFirstPointZero(arr2_rel)
                sn1_rel = absolute_relative.computeSnum(fz1_rel)
                sn2_rel = absolute_relative.computeSnum(fz2_rel)
                sis0_rel = absolute_relative.computeSi_S0(fz1_rel, fz2_rel)
                rel_degree = (1.0 + sn1_rel + sn2_rel) / (1.0 + sn1_rel + sn2_rel + sis0_rel)
                synthesis_degree = self.weight * abs_degree + (1.0 - self.weight) * rel_degree
                results.append(f"{num}: Calculation of synthesis degree of incidence for Sequence between [{i + 1}] and [{j + 1}]\n\n")
                results.append(f"(1) Absolute degree between Sequence[{i + 1}] and Sequence[{j + 1}]: {abs_degree:.4f}\n")
                results.append(f"(2) Relative degree between Sequence[{i + 1}] and Sequence[{j + 1}]: {rel_degree:.4f}\n")
                results.append(f"(3) Synthesis degree with weight {self.weight}: {synthesis_degree:.4f}\n\n")
        return "".join(results)
