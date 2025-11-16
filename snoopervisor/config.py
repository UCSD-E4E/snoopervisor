from croniter import croniter
from dynaconf import Dynaconf, Validator

validators = [
    Validator("users.ignore", must_exist=True, is_type_of=list),
    Validator("watchers.cpu.enabled", must_exist=True, is_type_of=bool),
    Validator(
        "watchers.cpu.threshold",
        must_exist=True,
        is_type_of=int,
        when=Validator("watchers.cpu.enabled", eq=True),
    ),
    Validator(
        "watchers.cpu.schedule",
        must_exist=True,
        is_type_of=str,
        condition=lambda v: croniter.is_valid(v),
        when=Validator("watchers.cpu.enabled", eq=True),
    ),
    Validator("watchers.memory.enabled", must_exist=True, is_type_of=bool),
    Validator(
        "watchers.memory.threshold",
        must_exist=True,
        is_type_of=int,
        when=Validator("watchers.memory.enabled", eq=True),
    ),
    Validator(
        "watchers.memory.schedule",
        must_exist=True,
        is_type_of=str,
        condition=lambda v: croniter.is_valid(v),
        when=Validator("watchers.memory.enabled", eq=True),
    ),
]

settings = Dynaconf(
    envvar_prefix="SNOOP",
    environments=False,
    settings_files=["settings.toml", ".secrets.toml"],
    validators=validators,
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
