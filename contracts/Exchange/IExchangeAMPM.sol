pragma solidity ^0.5.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

interface IExchangeAMPM {

      function buy(uint256 _amount) external;

      function sell(uint256 _amount) external;

      function priceChange(int256 _difference) external returns (uint256);

      function lastPrice() external view returns (uint256, uint256);

      function getHistory(uint256 _id_prezzo) external view returns (uint256);

      function isOpen() external view returns (bool);

}
