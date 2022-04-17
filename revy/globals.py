from revy.storages import ASGIRefLocalStorage


__all__ = (
    'global_storage',
)


global_storage = ASGIRefLocalStorage()
