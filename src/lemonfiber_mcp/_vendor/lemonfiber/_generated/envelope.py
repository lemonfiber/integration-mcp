# Copyright (c) 2026 NightWorksIO
"""Every kind the server may send, and the envelope of any of them.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .kinds import (
    AdmissionEnvelope,
    AdoptionEnvelope,
    AlertEnvelope,
    AlertsEnvelope,
    ArchivesEnvelope,
    BackupEnvelope,
    BandwidthEnvelope,
    BesideEnvelope,
    BundleEnvelope,
    CapabilitiesEnvelope,
    CatalogueEnvelope,
    CertificateEnvelope,
    ClientsEnvelope,
    ConfigEnvelope,
    CredentialsEnvelope,
    DashboardEnvelope,
    DoctorEnvelope,
    ErrorEnvelope,
    FormsEnvelope,
    FrontDoorEnvelope,
    GlossaryEnvelope,
    HandoffEnvelope,
    HeldEnvelope,
    HistoryEnvelope,
    HostingEnvelope,
    HouseholdEnvelope,
    ImportEnvelope,
    InvitationEnvelope,
    JobEnvelope,
    KeysEnvelope,
    LifecycleEnvelope,
    LogEnvelope,
    MigrationEnvelope,
    MintedKeyEnvelope,
    MusicEnvelope,
    NewsEnvelope,
    NewsItemsEnvelope,
    OutboundEnvelope,
    PairingEnvelope,
    PausingEnvelope,
    PlayingEnvelope,
    PluginsEnvelope,
    PreviewEnvelope,
    ProvenanceEnvelope,
    PullEnvelope,
    QualityEnvelope,
    RemovalEnvelope,
    RepairEnvelope,
    ReplacementEnvelope,
    ResetEnvelope,
    RestoreEnvelope,
    SeedEnvelope,
    SelfUpdateEnvelope,
    SetupEnvelope,
    SpaceEnvelope,
    StartEnvelope,
    StatusEnvelope,
    StepEnvelope,
    StopSeedingEnvelope,
    StoredEnvelope,
    StuckEnvelope,
    SubstitutionEnvelope,
    TraceEnvelope,
    UndoEnvelope,
    UninstallEnvelope,
    UpdateEnvelope,
    UpgradeEnvelope,
    VersionEnvelope,
    WalkthroughEnvelope,
    WatchEnvelope,
    WiringEnvelope,
    WizardEnvelope,
    WordEnvelope,
)

CONTRACT_API_VERSION: typing.Final = 1
"""The wire version these shapes were generated for."""

type Kind = typing.Literal[
    "admission",
    "adoption",
    "alert",
    "alerts",
    "archives",
    "backup",
    "bandwidth",
    "beside",
    "bundle",
    "capabilities",
    "catalogue",
    "certificate",
    "clients",
    "config",
    "credentials",
    "dashboard",
    "doctor",
    "error",
    "forms",
    "front-door",
    "glossary",
    "handoff",
    "held",
    "history",
    "hosting",
    "household",
    "import",
    "invitation",
    "job",
    "keys",
    "lifecycle",
    "log",
    "migration",
    "minted-key",
    "music",
    "news",
    "news-items",
    "outbound",
    "pairing",
    "pausing",
    "playing",
    "plugins",
    "preview",
    "provenance",
    "pull",
    "quality",
    "removal",
    "repair",
    "replacement",
    "reset",
    "restore",
    "seed",
    "self-update",
    "setup",
    "space",
    "start",
    "status",
    "step",
    "stop-seeding",
    "stored",
    "stuck",
    "substitution",
    "trace",
    "undo",
    "uninstall",
    "update",
    "upgrade",
    "version",
    "walkthrough",
    "watch",
    "wiring",
    "wizard",
    "word",
]
"""The name of every kind the server may send."""

KINDS: typing.Final[frozenset[Kind]] = frozenset(typing.get_args(Kind.__value__))
"""Every kind the server may send."""

type Envelope = (
    AdmissionEnvelope
    | AdoptionEnvelope
    | AlertEnvelope
    | AlertsEnvelope
    | ArchivesEnvelope
    | BackupEnvelope
    | BandwidthEnvelope
    | BesideEnvelope
    | BundleEnvelope
    | CapabilitiesEnvelope
    | CatalogueEnvelope
    | CertificateEnvelope
    | ClientsEnvelope
    | ConfigEnvelope
    | CredentialsEnvelope
    | DashboardEnvelope
    | DoctorEnvelope
    | ErrorEnvelope
    | FormsEnvelope
    | FrontDoorEnvelope
    | GlossaryEnvelope
    | HandoffEnvelope
    | HeldEnvelope
    | HistoryEnvelope
    | HostingEnvelope
    | HouseholdEnvelope
    | ImportEnvelope
    | InvitationEnvelope
    | JobEnvelope
    | KeysEnvelope
    | LifecycleEnvelope
    | LogEnvelope
    | MigrationEnvelope
    | MintedKeyEnvelope
    | MusicEnvelope
    | NewsEnvelope
    | NewsItemsEnvelope
    | OutboundEnvelope
    | PairingEnvelope
    | PausingEnvelope
    | PlayingEnvelope
    | PluginsEnvelope
    | PreviewEnvelope
    | ProvenanceEnvelope
    | PullEnvelope
    | QualityEnvelope
    | RemovalEnvelope
    | RepairEnvelope
    | ReplacementEnvelope
    | ResetEnvelope
    | RestoreEnvelope
    | SeedEnvelope
    | SelfUpdateEnvelope
    | SetupEnvelope
    | SpaceEnvelope
    | StartEnvelope
    | StatusEnvelope
    | StepEnvelope
    | StopSeedingEnvelope
    | StoredEnvelope
    | StuckEnvelope
    | SubstitutionEnvelope
    | TraceEnvelope
    | UndoEnvelope
    | UninstallEnvelope
    | UpdateEnvelope
    | UpgradeEnvelope
    | VersionEnvelope
    | WalkthroughEnvelope
    | WatchEnvelope
    | WiringEnvelope
    | WizardEnvelope
    | WordEnvelope
)
"""The envelope of any kind, told apart by its `kind`."""


__all__ = [
    "CONTRACT_API_VERSION",
    "Envelope",
    "KINDS",
    "Kind",
]
