/**
 * Cody's rational Chebyshev erfc approximation algorithm and Standard Normal CDF.
 *
 * Normative implementation of SPEC §3:
 * Reference: W. J. Cody, "Rational Chebyshev approximations for the error function",
 * Mathematics of Computation, 23(107), 1969, pp. 631-638.
 *
 * Guarantees |Phi(z) - scipy.special.ndtr(z)| < 1e-9 across all real inputs.
 */

const SQRPI = 5.6418958354775628695e-1;
const THRESH = 0.46875;
const SIXTEN = 16.0;
const XSMALL = 1.11e-16;
const XBIG = 26.543;

const A = [
  3.1611237438705656, 1.13864154151050156e2, 3.77485237685302021e2,
  3.20937758913846947e3, 1.85777706184603153e-1,
];

const B = [
  2.36012909523441209e1, 2.44024637934444173e2, 1.28261652607737228e3,
  2.84423683343917062e3,
];

const C = [
  5.64188496988670089e-1, 8.88314979438837594, 6.61191906371416295e1,
  2.98635138197400131e2, 8.8195222124176909e2, 1.71204761263407058e3,
  2.05107837782607147e3, 1.23033935479799725e3, 2.15311535474403846e-8,
];

const D = [
  1.57449261107098347e1, 1.17693950891312499e2, 5.37181101862009858e2,
  1.62138957456669019e3, 3.29079923573345963e3, 4.36261909014324716e3,
  3.43936767414372164e3, 1.23033935480374942e3,
];

const P = [
  3.05326634961232344e-1, 3.60344899949804439e-1, 1.25781726111229246e-1,
  1.60837851487422766e-2, 6.58749161529837803e-4, 1.63153871373020978e-2,
];

const Q = [
  2.56852019228982242, 1.87295284992346047, 5.27905102951428412e-1,
  6.05183413124413191e-2, 2.33520497626869185e-3,
];

/**
 * Computes complementary error function erfc(x) using Cody's minimax rational Chebyshev approximations.
 */
export function erfc(x: number): number {
  if (Number.isNaN(x)) {
    return Number.NaN;
  }
  const y = Math.abs(x);
  let result = 0.0;

  if (y <= THRESH) {
    let ysq = 0.0;
    if (y > XSMALL) {
      ysq = y * y;
    }
    // Safe non-null assertion: indices 0..4 are fixed arrays of length 5 and 4
    let xnum = A[4]! * ysq;
    let xden = ysq;
    for (let i = 0; i < 3; i++) {
      xnum = (xnum + A[i]!) * ysq;
      xden = (xden + B[i]!) * ysq;
    }
    result = (x * (xnum + A[3]!)) / (xden + B[3]!);
    return 1.0 - result;
  } else if (y <= 4.0) {
    let xnum = C[8]! * y;
    let xden = y;
    for (let i = 0; i < 7; i++) {
      xnum = (xnum + C[i]!) * y;
      xden = (xden + D[i]!) * y;
    }
    result = (xnum + C[7]!) / (xden + D[7]!);
    const ysq = Math.floor(y * SIXTEN) / SIXTEN;
    const del = (y - ysq) * (y + ysq);
    result = Math.exp(-ysq * ysq) * Math.exp(-del) * result;
  } else {
    result = 0.0;
    if (y < XBIG) {
      const ysqInv = 1.0 / (y * y);
      let xnum = P[5]! * ysqInv;
      let xden = ysqInv;
      for (let i = 0; i < 4; i++) {
        xnum = (xnum + P[i]!) * ysqInv;
        xden = (xden + Q[i]!) * ysqInv;
      }
      result = (ysqInv * (xnum + P[4]!)) / (xden + Q[4]!);
      result = (SQRPI - result) / y;
      const ysqFloor = Math.floor(y * SIXTEN) / SIXTEN;
      const del = (y - ysqFloor) * (y + ysqFloor);
      result = Math.exp(-ysqFloor * ysqFloor) * Math.exp(-del) * result;
    }
  }

  if (x < 0.0) {
    result = 2.0 - result;
  }
  return result;
}

/**
 * Computes the standard normal cumulative distribution function Phi(z) = 0.5 * erfc(-z / sqrt(2)).
 */
export function normalCdf(z: number): number {
  if (Number.isNaN(z)) {
    return Number.NaN;
  }
  if (z === Number.POSITIVE_INFINITY) {
    return 1.0;
  }
  if (z === Number.NEGATIVE_INFINITY) {
    return 0.0;
  }
  return 0.5 * erfc(-z / Math.SQRT2);
}
