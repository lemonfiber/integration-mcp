# Copyright (c) 2026 NightWorksIO
"""The signature that narrows an envelope to one kind.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .envelope import Envelope
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


class KindNarrowing(typing.Protocol):
    """Narrows an envelope to the one kind it is expected to be."""

    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["admission"], /) -> AdmissionEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["adoption"], /) -> AdoptionEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["alert"], /) -> AlertEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["alerts"], /) -> AlertsEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["archives"], /) -> ArchivesEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["backup"], /) -> BackupEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["bandwidth"], /) -> BandwidthEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["beside"], /) -> BesideEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["bundle"], /) -> BundleEnvelope: ...
    @typing.overload
    def __call__(
        self, envelope: Envelope, kind: typing.Literal["capabilities"], /
    ) -> CapabilitiesEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["catalogue"], /) -> CatalogueEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["certificate"], /) -> CertificateEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["clients"], /) -> ClientsEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["config"], /) -> ConfigEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["credentials"], /) -> CredentialsEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["dashboard"], /) -> DashboardEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["doctor"], /) -> DoctorEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["error"], /) -> ErrorEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["forms"], /) -> FormsEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["front-door"], /) -> FrontDoorEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["glossary"], /) -> GlossaryEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["handoff"], /) -> HandoffEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["held"], /) -> HeldEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["history"], /) -> HistoryEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["hosting"], /) -> HostingEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["household"], /) -> HouseholdEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["import"], /) -> ImportEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["invitation"], /) -> InvitationEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["job"], /) -> JobEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["keys"], /) -> KeysEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["lifecycle"], /) -> LifecycleEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["log"], /) -> LogEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["migration"], /) -> MigrationEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["minted-key"], /) -> MintedKeyEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["music"], /) -> MusicEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["news"], /) -> NewsEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["news-items"], /) -> NewsItemsEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["outbound"], /) -> OutboundEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["pairing"], /) -> PairingEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["pausing"], /) -> PausingEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["playing"], /) -> PlayingEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["plugins"], /) -> PluginsEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["preview"], /) -> PreviewEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["provenance"], /) -> ProvenanceEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["pull"], /) -> PullEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["quality"], /) -> QualityEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["removal"], /) -> RemovalEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["repair"], /) -> RepairEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["replacement"], /) -> ReplacementEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["reset"], /) -> ResetEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["restore"], /) -> RestoreEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["seed"], /) -> SeedEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["self-update"], /) -> SelfUpdateEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["setup"], /) -> SetupEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["space"], /) -> SpaceEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["start"], /) -> StartEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["status"], /) -> StatusEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["step"], /) -> StepEnvelope: ...
    @typing.overload
    def __call__(
        self, envelope: Envelope, kind: typing.Literal["stop-seeding"], /
    ) -> StopSeedingEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["stored"], /) -> StoredEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["stuck"], /) -> StuckEnvelope: ...
    @typing.overload
    def __call__(
        self, envelope: Envelope, kind: typing.Literal["substitution"], /
    ) -> SubstitutionEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["trace"], /) -> TraceEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["undo"], /) -> UndoEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["uninstall"], /) -> UninstallEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["update"], /) -> UpdateEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["upgrade"], /) -> UpgradeEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["version"], /) -> VersionEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["walkthrough"], /) -> WalkthroughEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["watch"], /) -> WatchEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["wiring"], /) -> WiringEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["wizard"], /) -> WizardEnvelope: ...
    @typing.overload
    def __call__(self, envelope: Envelope, kind: typing.Literal["word"], /) -> WordEnvelope: ...


__all__ = [
    "KindNarrowing",
]
