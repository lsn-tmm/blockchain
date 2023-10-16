pragma solidity ^0.5.0;

import "@openzeppelin/contracts/math/SafeMath.sol";


contract Example {
   using SafeMath for uint256;

   function sum(uint256 a, uint256 b) public view returns (uint256) {
      return a.add(b);
   }
}
