from worlds.LauncherComponents import Component, Type, components, launch, SuffixIdentifier

from .rom import PBRPatch


def run_client(*args: str) -> None:
    from .pbr_client import main

    launch(main, name="Pokémon Battle Revolution Client", args=args)


components.append(
    Component(
        "Pokémon Battle Revolution Client",
        func=run_client,
        component_type=Type.CLIENT,
        file_identifier=SuffixIdentifier(".appbr"),
    )
)