---
title: "Correlation ID vs Request ID: A Practical Guide"
published:
tags: observability, distributedsystems, backend, debugging
cover_image:
---

A request hits your API. Your service calls two others. One of them calls two more. The first downstream call times out, so you retry. Something fails. You open the logs.

Can you trace the full journey end-to-end? Can you tell which entries are the retry?

Two identifiers answer these questions.

**Correlation ID** links everything across an end-to-end flow. It stays the same from the first inbound request through every downstream call. **Request ID** identifies a single hop. Each outbound call gets its own. Retry a call, and you get the same correlation ID under a new request ID.

They complement each other, and understanding the distinction is the difference between logs that help and logs that taunt.

I've built this pattern more than once. Each time, I went looking for one good article to send the team and came up short -- every piece I liked either stayed in reference-doc weeds or pivoted straight to OpenTelemetry traces. None reached for the analogy that made it click for me. So I wrote the one I wish I'd had.

## The kitchen

Picture a kitchen brigade:

- **Chef** -- gets the ticket, calls SousChef and LineCook
- **SousChef** -- handles recipes, delegates to PrepCook and DishWasher
- **LineCook** -- executes the dish
- **PrepCook** -- prepares ingredients
- **DishWasher** -- provides clean plates

![Kitchen brigade](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/4wxyp0hip7o6il7k8pyh.png)

### The ticket and the shout

The **table ticket** is your correlation ID. Table 4's ticket stays pinned to the rail from the moment the waiter clips it there until the dish goes out. Every station reads the same ticket number. PrepCook knows it's for table 4. LineCook knows it's for table 4. Nobody asks *which table is this for?* because the ticket never changes hands.

Each **shout** between stations is a request ID. When Chef shouts "Fire table 4, two salmon!", that shout gets its own identifier. If LineCook doesn't respond, Chef shouts again -- same ticket, new shout.

## Mise en place

In a kitchen, mise en place means prepping and organizing every ingredient before the first pan hits the flame. When service starts, you reach for what you need without thinking. Our code needs the same.

`CorrelationId` and `RequestId` are [Value Objects](https://vimeo.com/13549100): tiny, immutable wrappers. Pass a ticket ID where a shout ID belongs and the compiler stops you.

```ts
class CorrelationId {
  private constructor(private readonly value: string) {}
  static create(): CorrelationId { return new CorrelationId(uuid()); }
  static fromString(value: string): CorrelationId { return new CorrelationId(value); }
  toString(): string { return this.value; }
}

class RequestId {
  private constructor(private readonly value: string) {}
  static create(): RequestId { return new RequestId(uuid()); }
  static fromString(value: string): RequestId { return new RequestId(value); }
  toString(): string { return this.value; }
}
```

The other half of mise en place is making these available everywhere without passing them around. The middleware at the boundary pushes them into two places:

1. **Async-local context**: [OpenTelemetry's `AsyncLocalStorageContextManager`](https://www.npmjs.com/package/@opentelemetry/context-async-hooks) wraps execution so `ExecutionContext.correlationId` and `ExecutionContext.requestId` behave like globals within the async call chain. (It's the modern successor to `AsyncHooksContextManager` and requires a recent Node runtime.) At the boundary, a call to `ExecutionContext.run(...)` populates the context; any code downstream reads from it without needing the IDs passed explicitly.

2. **The logging tooling**: The logger is `ExecutionContext`-aware: every log entry automatically carries `correlationId` and `requestId`. In the examples below, `log.info()` only passes extra context like `fn` or `url` -- the core IDs are added automatically, as the inline comment notes.

Business code rarely touches `ExecutionContext` directly. It just logs what it's doing. The IDs are present on every entry, searchable and filterable, without a single explicit reference in the business logic.

The examples below use UUID v4. Whether that's the right format for your system is a separate question — [Hilton's article on microservice correlation IDs](https://hilton.org.uk/blog/microservices-correlation-id) covers the tradeoffs.

## Tickets from the front of house (your public API)

A request lands at your public API. You generate both IDs yourself. Accepting an external caller's correlation ID or request ID means relaying uncontrolled data into your internal logs. A buggy client sending `x-correlation-id: foo` for every request pollutes every downstream service's logs with the same value. Same goes for `x-request-id`.

```js
// Public API middleware
app.use('/api/public', (req, res, next) => {
  const externalCorrelationId = req.headers['x-correlation-id']; // remembered, not used
  const externalRequestId = req.headers['x-request-id']; // remembered, not used
  const correlationId = CorrelationId.create().toString(); // our table ticket
  const requestId = RequestId.create().toString(); // our shout

  res.setHeader('x-correlation-id', externalCorrelationId || correlationId); // echo back theirs
  res.setHeader('x-request-id', externalRequestId || requestId);

  ExecutionContext.run({ correlationId, requestId }, () => {
    // correlationId and requestId are automatically added to every log entry by the logging tooling
    log.info({ fn: 'publicApiMiddleware' }, 'request received');
    next();
  });
});
```

Echoing the caller's original IDs back on the response is a nicety: they get their IDs back for their own tracing, but your logs stay clean. You can also add `x-correlation-id-internal` and `x-request-id-internal` response headers with the IDs you used internally so callers can reference them when reporting issues. The tradeoff: this exposes internal identifiers, which some organizations consider a data leak.

## Your own crew (your internal API)

When all your callers are your own kitchen stations, accepting their request ID lets them grep your logs when SousChef asks why the steak showed up instead of the salmon (debugging a failed request), when the manager wants to know why the salmon went out cold (latency investigation), or when the health inspector wants the full ticket timeline (audit).

```js
// Internal API middleware
app.use('/api/internal', (req, res, next) => {
  const correlationId = req.headers['x-correlation-id'] || CorrelationId.create().toString();
  const requestId = req.headers['x-request-id'] || RequestId.create().toString(); // trust the crew's shout

  res.setHeader('x-correlation-id', correlationId);
  res.setHeader('x-request-id', requestId);

  ExecutionContext.run({ correlationId, requestId }, () => {
    // correlationId and requestId are automatically added to every log entry by the logging tooling
    log.info({ fn: 'internalApiMiddleware' }, 'request received');
    next();
  });
});
```

Both middlewares fit in the same app, each scoped to its own route group. The boundary between internal and external is already in your route registration.

The table ticket (correlation ID) is the cross-station link. The trust decision is structural -- once you've drawn the line in your route registration, you don't make it again at every request.

## Shouts across the stations (your internal outbound calls)

Every time Chef calls out to another station, the table ticket (correlation ID) gets forwarded but the shout (request ID) is always new -- generated *before* the call goes out so you have an ID to log against even if the call times out. Because `ExecutionContext.run(...)` was called at the inbound boundary, the correlation ID is globally available -- the interceptor reads it without needing `req` in scope.

```js
// Axios outbound interceptor
axios.interceptors.request.use((config) => {
  const correlationId = ExecutionContext.correlationId?.toString() || CorrelationId.create().toString(); // same table ticket, or a fresh one if no inbound context
  const outboundRequestId = RequestId.create().toString(); // new shout, local to this hop

  // The auto-added requestId is still the INBOUND one (the logger pulls from
  // ExecutionContext); log outboundRequestId explicitly so this hop is traceable.
  log.info({ fn: 'outboundInterceptor', url: config.url, outboundRequestId }, 'outbound call');

  config.headers['x-correlation-id'] = correlationId;
  config.headers['x-request-id'] = outboundRequestId;

  return config;
});
```

One subtle thing about the log line above: `log.info()` auto-injects the `requestId` from `ExecutionContext`, which is still the **inbound** request ID (the inbound call hasn't finished yet -- we're mid-flight). The new outbound ID lives only in this function's local scope, so passing it as `requestId` would get overridden by the logger's auto-injection. Log it under a different key (`outboundRequestId` above) and it sits alongside the auto-injected fields without colliding. From the downstream service's perspective the same ID lands as `x-request-id` on the wire and becomes their inbound `requestId` -- the "outbound" qualifier is only meaningful here, on the caller side.

Chef clips ticket-4 to the rail. "Fire table 4, two salmon!" LineCook is buried under a stack of tickets, three pans going. No response. Chef shouts again, louder. Still nothing. Third call, LineCook finally yells back "Heard!" Each shout lands in the log under the same ticket number (correlation ID) with a fresh shout ID (request ID).

![Shout retry](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/zr862mqi9kz3roqnrr71.png)

*Shout IDs above are numbered from 1 for clarity. In the full trace at the end of the article, they follow the global sequence across all five stations.*

## Orders to the suppliers (your external outbound calls)

Sometimes Chef needs ingredients the kitchen doesn't make. The bread comes from the bakery, the fish from the fishmonger, the produce from the market. When Chef calls the fishmonger to order 5 lbs of salmon by 10am, the kitchen's internal table ticket is irrelevant to the fishmonger -- and forwarding it would tell them more about your operation than they need to know.

The same applies to outbound HTTP calls to third-party APIs (payment processors, mapping services, vendor integrations). Forwarding your internal `x-correlation-id` and `x-request-id` headers to an external service leaks information about your request flow into a system that doesn't need it, and may store it in their logs indefinitely. Scope the outbound interceptor to your internal HTTP clients only, or add a URL allowlist that excludes external hosts.

If the third-party returns its own correlation or request ID on the response, record it on your side. It's the thread that ties your logs to theirs when you need to debug a cross-system issue.

## Takeout orders (async messaging)

The pattern above is HTTP-shaped, but the boundary is the only thing that matters. A Kafka consumer, SQS handler, or Kinesis processor pulls the correlation ID out of message headers or record metadata, calls `ExecutionContext.run(...)`, and from there the rest of the code is identical. The transport changes; the approach doesn't.

## One trace, one picture

Five stations, one table ticket. The correlation ID is the value that doesn't change. The request ID is the value that does -- every shout from Chef to a station gets its own, every retry gets a fresh one, every downstream call too. Read the trace by following the correlation ID down the page; read the retries by spotting the request IDs that bunch up under the same correlation ID.

![Full Sequence](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/ja3oq4ojxd57287n0ylk.png)

## When this stops being enough

This pattern -- correlation ID at the boundary, request ID per hop, both on every log line -- holds up until your system grows in complexity. When the debugging question becomes *where in this 14-service flow did 80% of the latency get spent?*, you've outgrown correlation IDs and you want OpenTelemetry traces. Last9's piece on correlation ID vs trace ID (in [References](#references) below) is the right next read for that step -- it goes deeper into trace IDs than this article wanted to.

## Same name, different recipe

`x-correlation-id` is used differently across the industry. This article treats it as a trace ID -- fresh per inbound boundary entry, propagated across downstream calls. [Adobe's API](https://developer.adobe.com/vipmp/docs/references/idempotency) uses it as an idempotency key instead -- a stable identifier the client reuses across retries of the same business intent so the server can return the cached response. The two uses are incompatible. If you're integrating with a service that enforces idempotency on `x-correlation-id`, pick a different header (or namespace your own) for the trace ID described here. [Stripe's `Idempotency-Key`](https://docs.stripe.com/api/idempotent_requests) is the cleaner pattern -- a dedicated header for idempotency, no collision with tracing.

## Start with the paring knife

Two value objects, one async-local context, an `ExecutionContext`-aware logger, a couple of middlewares, one interceptor. Reach for the cleaver when the system asks for it, not before. This is what worked in real systems -- search `correlation_id` in my [career changelog](https://ouimet.info/#career-changelog) to see where.

Open the logs. Filter by correlation ID and you have the journey. Filter by request ID and you have the one retry, alone, no noise.

## References

- [Microservices Correlation ID (Hilton)](https://hilton.org.uk/blog/microservices-correlation-id)
- [Idempotency (Adobe)](https://developer.adobe.com/vipmp/docs/references/idempotency)
- [Correlation ID vs Trace ID (Last9)](https://last9.io/blog/correlation-id-vs-trace-id/)
- [The Value of Correlation IDs (Rapid7)](https://www.rapid7.com/blog/post/2016/12/23/the-value-of-correlation-ids/)
- [Correlation IDs in Enterprise Architecture (StreamZero)](https://medium.com/stream-zero/correlation-ids-in-enterprise-architecture-d5851df23da0)
- [How I Added Multi-Threaded Features to Express.js (Hackernoon)](https://medium.com/hackernoon/how-i-added-awesome-multi-threaded-features-to-express-js-753452a1c10e)
- [Correlation IDs: End-to-End Tracing (Koder)](https://koder.ai/blog/correlation-ids-end-to-end-tracing)
- [Microservice Error Tracing Using Correlation IDs (Realtor.com)](https://techblog.realtor.com/microservice-error-tracing-using-correlation-ids/)
- [Logging Request IDs and Correlation IDs (use.id)](https://docs.use.id/docs/logging-request-ids-and-correlation-ids)
