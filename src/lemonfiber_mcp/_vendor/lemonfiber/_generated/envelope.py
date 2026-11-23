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
    AskableEnvelope,
    AskableKindsEnvelope,
    AskedEnvelope,
    BackupEnvelope,
    BandwidthEnvelope,
    BesideEnvelope,
    BootEnvelope,
    BundleEnvelope,
    CallerEnvelope,
    CapabilitiesEnvelope,
    CatalogueEnvelope,
    CertificateEnvelope,
    ChannelsEnvelope,
    ClientsEnvelope,
    ConfigEnvelope,
    CredentialsEnvelope,
    DashboardEnvelope,
    DeviceChallengeEnvelope,
    DeviceKeyEnvelope,
    DeviceKeysEnvelope,
    DoctorEnvelope,
    EndedEnvelope,
    ErrorEnvelope,
    FormsEnvelope,
    FrontDoorEnvelope,
    GlossaryEnvelope,
    GrantEnvelope,
    GuideEnvelope,
    HandoffEnvelope,
    HeldEnvelope,
    HistoryEnvelope,
    HostingEnvelope,
    HouseholdEnvelope,
    ImportEnvelope,
    InFlightEnvelope,
    InvitationEnvelope,
    JobEnvelope,
    KeyClaimEnvelope,
    KeysEnvelope,
    LifecycleEnvelope,
    LogEnvelope,
    LogsEnvelope,
    MigrationEnvelope,
    MintedKeyEnvelope,
    MusicEnvelope,
    NewsEnvelope,
    NewsItemsEnvelope,
    NotifyEnvelope,
    NotifyMineEnvelope,
    OutboundEnvelope,
    PairingEnvelope,
    PartWayEnvelope,
    PasswordEnvelope,
    PausingEnvelope,
    PlayEnvelope,
    PlayingEnvelope,
    PluginCatalogueEnvelope,
    PluginClaimsEnvelope,
    PluginConformanceEnvelope,
    PluginProvenanceEnvelope,
    PluginRecordingEnvelope,
    PluginsEnvelope,
    PreviewEnvelope,
    ProvenanceEnvelope,
    PullEnvelope,
    PushEndpointEnvelope,
    PushEndpointsEnvelope,
    QualityEnvelope,
    QueueEnvelope,
    RanEnvelope,
    RemovalEnvelope,
    RepairEnvelope,
    ReplacementEnvelope,
    ResetEnvelope,
    RestoreEnvelope,
    SeedEnvelope,
    SelfUpdateEnvelope,
    ServedEnvelope,
    SettingsEnvelope,
    SettledEnvelope,
    SetupEnvelope,
    SignInCodeEnvelope,
    SpaceEnvelope,
    StackEnvelope,
    StandingEnvelope,
    StartEnvelope,
    StatusEnvelope,
    StepEnvelope,
    StopSeedingEnvelope,
    StoredEnvelope,
    StuckEnvelope,
    SubstitutionEnvelope,
    TitleEnvelope,
    TraceEnvelope,
    TunedEnvelope,
    UndoEnvelope,
    UninstallEnvelope,
    UpdateEnvelope,
    UpgradeEnvelope,
    VersionEnvelope,
    WalkthroughEnvelope,
    WalkthroughOfferEnvelope,
    WatchEnvelope,
    WatchedEnvelope,
    WatcherEnvelope,
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
    "askable",
    "askable-kinds",
    "asked",
    "backup",
    "bandwidth",
    "beside",
    "boot",
    "bundle",
    "caller",
    "capabilities",
    "catalogue",
    "certificate",
    "channels",
    "clients",
    "config",
    "credentials",
    "dashboard",
    "device-challenge",
    "device-key",
    "device-keys",
    "doctor",
    "ended",
    "error",
    "forms",
    "front-door",
    "glossary",
    "grant",
    "guide",
    "handoff",
    "held",
    "history",
    "hosting",
    "household",
    "import",
    "in-flight",
    "invitation",
    "job",
    "key-claim",
    "keys",
    "lifecycle",
    "log",
    "logs",
    "migration",
    "minted-key",
    "music",
    "news",
    "news-items",
    "notify",
    "notify-mine",
    "outbound",
    "pairing",
    "part-way",
    "password",
    "pausing",
    "play",
    "playing",
    "plugin-catalogue",
    "plugin-claims",
    "plugin-conformance",
    "plugin-provenance",
    "plugin-recording",
    "plugins",
    "preview",
    "provenance",
    "pull",
    "push-endpoint",
    "push-endpoints",
    "quality",
    "queue",
    "ran",
    "removal",
    "repair",
    "replacement",
    "reset",
    "restore",
    "seed",
    "self-update",
    "served",
    "settings",
    "settled",
    "setup",
    "sign-in-code",
    "space",
    "stack",
    "standing",
    "start",
    "status",
    "step",
    "stop-seeding",
    "stored",
    "stuck",
    "substitution",
    "title",
    "trace",
    "tuned",
    "undo",
    "uninstall",
    "update",
    "upgrade",
    "version",
    "walkthrough",
    "walkthrough-offer",
    "watch",
    "watched",
    "watcher",
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
    | AskableEnvelope
    | AskableKindsEnvelope
    | AskedEnvelope
    | BackupEnvelope
    | BandwidthEnvelope
    | BesideEnvelope
    | BootEnvelope
    | BundleEnvelope
    | CallerEnvelope
    | CapabilitiesEnvelope
    | CatalogueEnvelope
    | CertificateEnvelope
    | ChannelsEnvelope
    | ClientsEnvelope
    | ConfigEnvelope
    | CredentialsEnvelope
    | DashboardEnvelope
    | DeviceChallengeEnvelope
    | DeviceKeyEnvelope
    | DeviceKeysEnvelope
    | DoctorEnvelope
    | EndedEnvelope
    | ErrorEnvelope
    | FormsEnvelope
    | FrontDoorEnvelope
    | GlossaryEnvelope
    | GrantEnvelope
    | GuideEnvelope
    | HandoffEnvelope
    | HeldEnvelope
    | HistoryEnvelope
    | HostingEnvelope
    | HouseholdEnvelope
    | ImportEnvelope
    | InFlightEnvelope
    | InvitationEnvelope
    | JobEnvelope
    | KeyClaimEnvelope
    | KeysEnvelope
    | LifecycleEnvelope
    | LogEnvelope
    | LogsEnvelope
    | MigrationEnvelope
    | MintedKeyEnvelope
    | MusicEnvelope
    | NewsEnvelope
    | NewsItemsEnvelope
    | NotifyEnvelope
    | NotifyMineEnvelope
    | OutboundEnvelope
    | PairingEnvelope
    | PartWayEnvelope
    | PasswordEnvelope
    | PausingEnvelope
    | PlayEnvelope
    | PlayingEnvelope
    | PluginCatalogueEnvelope
    | PluginClaimsEnvelope
    | PluginConformanceEnvelope
    | PluginProvenanceEnvelope
    | PluginRecordingEnvelope
    | PluginsEnvelope
    | PreviewEnvelope
    | ProvenanceEnvelope
    | PullEnvelope
    | PushEndpointEnvelope
    | PushEndpointsEnvelope
    | QualityEnvelope
    | QueueEnvelope
    | RanEnvelope
    | RemovalEnvelope
    | RepairEnvelope
    | ReplacementEnvelope
    | ResetEnvelope
    | RestoreEnvelope
    | SeedEnvelope
    | SelfUpdateEnvelope
    | ServedEnvelope
    | SettingsEnvelope
    | SettledEnvelope
    | SetupEnvelope
    | SignInCodeEnvelope
    | SpaceEnvelope
    | StackEnvelope
    | StandingEnvelope
    | StartEnvelope
    | StatusEnvelope
    | StepEnvelope
    | StopSeedingEnvelope
    | StoredEnvelope
    | StuckEnvelope
    | SubstitutionEnvelope
    | TitleEnvelope
    | TraceEnvelope
    | TunedEnvelope
    | UndoEnvelope
    | UninstallEnvelope
    | UpdateEnvelope
    | UpgradeEnvelope
    | VersionEnvelope
    | WalkthroughEnvelope
    | WalkthroughOfferEnvelope
    | WatchEnvelope
    | WatchedEnvelope
    | WatcherEnvelope
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
