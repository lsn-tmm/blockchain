pragma solidity ^0.5.0;


import "@openzeppelin/contracts/token/ERC20/ERC20Mintable.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20Detailed.sol";

import "./ERC20Burnable.sol";
import "../Utils/roles/ManagerRole.sol";

contract AMPM is ManagerRole, ERC20Burnable, ERC20Mintable, ERC20Detailed("AMPM", "MPM", 18) {

  address payable private _owner;

    constructor() public {
      _owner = _msgSender();
    }

    function close() public onlyManager {
      selfdestruct(_owner);
    }

}
