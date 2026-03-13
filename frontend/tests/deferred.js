/**
 * Create a deferred promise for controlling async test timing.
 * @returns {{ promise: Promise, resolve: Function }}
 */
export function deferred() {
  let resolve;
  const promise = new Promise((res) => {
    resolve = res;
  });
  return { promise, resolve };
}
