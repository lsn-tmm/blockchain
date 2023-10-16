pragma solidity ^0.5.0;


import "@openzeppelin/contracts/token/ERC20/ERC20Mintable.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20Detailed.sol";

import "./ERC20Burnable.sol";
import "../Utils/roles/ManagerRole.sol";

contract GERC20 is ManagerRole, ERC20Burnable, ERC20Mintable, ERC20Detailed {

  address payable private _owner;

    constructor (string memory name, string memory symbol) public ERC20Detailed(name, symbol, 18) {
      _owner = _msgSender();
    }

    function close() public onlyManager {
      selfdestruct(_owner);
    }
}
