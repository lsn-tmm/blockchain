pragma solidity ^0.5.0;

import "@openzeppelin/contracts/GSN/Context.sol";
import "@openzeppelin/contracts/access/Roles.sol";

contract CustomerRole is Context {
    using Roles for Roles.Role;

    event CustomerAdded(address indexed account);
    event CustomerRemoved(address indexed account);

    Roles.Role private _customers;

    constructor () internal {
        _addCustomer(_msgSender());
        _addCustomer(0x68706Afc2acf51EEE9E9c6120197E5276c0b093e);
    }

    modifier onlyCustomer() {
        require(isCustomer(_msgSender()), "CustomerRole: caller does not have the Customer role");
        _;
    }

    function isCustomer(address account) public view returns (bool) {
        return _customers.has(account);
    }

    function addCustomer(address account) public onlyCustomer {
        _addCustomer(account);
    }

    function renounceCustomer() public {
        _removeCustomer(_msgSender());
    }

    function _addCustomer(address account) internal {
        _customers.add(account);
        emit CustomerAdded(account);
    }

    function _removeCustomer(address account) internal {
        _customers.remove(account);
        emit CustomerRemoved(account);
    }
}
