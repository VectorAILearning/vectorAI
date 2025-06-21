"""
Минимальный Dependency Injection контейнер.
Простая реализация без переусложнений для управления зависимостями сервисов.
"""

from typing import Any, Callable, Dict, Type, TypeVar

T = TypeVar("T")


class DIContainer:
    """
    Минимальный DI контейнер для управления созданием сервисов и их зависимостей.
    Поддерживает фабричные функции и простое кеширование.
    """

    def __init__(self):
        self._factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}

    def register_factory(self, service_type: Type[T], factory_func: Callable[..., T]):
        """
        Регистрирует фабричную функцию для создания сервиса.

        Args:
            service_type: Тип сервиса
            factory_func: Функция создания сервиса
        """
        self._factories[service_type] = factory_func

    def register_singleton(self, service_type: Type[T], instance: T):
        """
        Регистрирует синглтон объект.

        Args:
            service_type: Тип сервиса
            instance: Готовый экземпляр
        """
        self._singletons[service_type] = instance

    def get_service(self, service_type: Type[T], **kwargs) -> T:
        """
        Получает экземпляр сервиса.
        Сначала проверяет синглтоны, затем использует фабрику.

        Args:
            service_type: Тип запрашиваемого сервиса
            **kwargs: Аргументы для фабричной функции

        Returns:
            Экземпляр сервиса

        Raises:
            ValueError: Если сервис не зарегистрирован
        """
        # Проверяем синглтоны
        if service_type in self._singletons:
            return self._singletons[service_type]

        # Используем фабрику
        if service_type in self._factories:
            factory = self._factories[service_type]
            return factory(**kwargs)

        raise ValueError(
            f"Сервис {service_type.__name__} не зарегистрирован в контейнере"
        )

    def has_service(self, service_type: Type) -> bool:
        """
        Проверяет, зарегистрирован ли сервис.

        Args:
            service_type: Тип сервиса

        Returns:
            True если сервис зарегистрирован
        """
        return service_type in self._factories or service_type in self._singletons


# Глобальный экземпляр контейнера
container = DIContainer()
