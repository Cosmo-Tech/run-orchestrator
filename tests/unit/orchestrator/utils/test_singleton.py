import pytest

from cosmotech.orchestrator.utils.singleton import Singleton


class TestSingleton:
    def test_creates_single_instance(self):
        # Setup
        class TestClass(metaclass=Singleton):
            def __init__(self, value=None):
                self.value = value

        # Execute
        instance1 = TestClass(value="test1")
        instance2 = TestClass(value="test2")

        # Verify
        assert instance1 is instance2
        assert instance1.value == "test1"  # Second initialization should be ignored

    def test_different_classes_have_different_instances(self):
        # Setup
        class TestClass1(metaclass=Singleton):
            pass

        class TestClass2(metaclass=Singleton):
            pass

        # Execute
        instance1 = TestClass1()
        instance2 = TestClass2()

        # Verify
        assert instance1 is not instance2
        assert isinstance(instance1, TestClass1)
        assert isinstance(instance2, TestClass2)

    def test_subclasses_have_different_instances(self):
        # Setup
        class BaseClass(metaclass=Singleton):
            pass

        class SubClass(BaseClass):
            pass

        # Execute
        base_instance = BaseClass()
        sub_instance = SubClass()

        # Verify
        assert base_instance is not sub_instance
        assert isinstance(base_instance, BaseClass)
        assert isinstance(sub_instance, SubClass)

    def test_instances_persist_across_calls(self):
        # Setup
        class TestClass(metaclass=Singleton):
            def __init__(self):
                self.counter = 0

            def increment(self):
                self.counter += 1

        # Execute
        instance1 = TestClass()
        instance1.increment()
        instance2 = TestClass()

        # Verify
        assert instance1 is instance2
        assert instance1.counter == 1
        assert instance2.counter == 1
