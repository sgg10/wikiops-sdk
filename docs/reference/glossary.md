# Glossary

## Apply Result

The aggregate result returned by a provider after attempting to apply a `ChangeSet`.

## ChangeSet

The provider-agnostic plan returned by a plugin. It contains operations plus optional warnings and notes.

## Compatibility Policy

The rule used to decide whether one API version is compatible with another. The default SDK policy is `same_major`.

## Documentation Plugin

An extension that contains business logic for planning documentation changes.

## Document

The portable SDK model representing document content, title, format, version, and metadata.

## Document Provider

An extension that reads and persists documents in a concrete wiki backend.

## DocumentRef

A portable reference to a document, including provider namespace, reference kind, and locator data.

## DocumentVersion

Provider-agnostic version metadata used for optimistic concurrency checks.

## Entry Point Group

The canonical name used by the host to discover plugins or providers. The SDK reserves `wikiops.plugins` and `wikiops.providers`.

## ExecutionContext

Mutable runtime state shared during orchestration and plugin planning.

## Host

The runtime application that loads plugins and providers, validates compatibility, builds context, and coordinates execution. This is not implemented in this repository.

## NoteMessage

Structured informational message attached to a `ChangeSet`.

## Operation

A planned mutation such as create, update, or create child document.

## Plugin Resource Provider

The read-only contract a plugin uses to access files packaged with the plugin itself.

## Provider Capability

An advertised feature flag indicating what a provider can do.

## Strict Compatibility Mode

The SDK mode in which omitted API versions are treated as errors instead of being resolved implicitly.

## WarningMessage

Structured warning attached to a `ChangeSet`.

## WikiOps

The broader ecosystem that treats documentation as code and aims to automate Markdown-based documentation workflows across multiple wiki platforms.
