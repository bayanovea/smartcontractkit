from brownie import accounts, SimpleStorage


def test_deploy():
    account = accounts[0]

    simple_storage = SimpleStorage.deploy({"from": account})
    starting_value = simple_storage.retrieve()
    excepted_value = 0

    assert starting_value == excepted_value


def test_updating_storage():
    account = accounts[0]

    simple_storage = SimpleStorage.deploy({"from": account})
    excepted_value = 15
    simple_storage.store(excepted_value, {"from": account})
    updated_value = simple_storage.retrieve()

    assert updated_value == excepted_value
