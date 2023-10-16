pragma solidity ^0.5.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20Mintable.sol";
import "../ERC20/ERC20Burnable.sol";

import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import "@openzeppelin/contracts/math/SafeMath.sol";
import "../Utils/time/BokkyPooBahsDateTimeLibrary.sol";

import "../Utils/roles/CustomerRole.sol";
import "../Utils/roles/ManagerRole.sol";

contract Lender is CustomerRole, ManagerRole {
  using SafeMath for uint256;
  using SafeERC20 for IERC20;
  using BokkyPooBahsDateTimeLibrary for uint256;

  // The token being sold
  IERC20 private _paycoin;

  address payable private _owner;

  uint256 private _end;

  struct Loan {
    bool _open;
    uint256 _amount;
    uint256 _block;
  }

  uint private _nonce = 0; // Seed to random numbers
  uint private _max_loan = 250000 * 10**18;

  mapping ( address => mapping ( uint256 => Loan ) ) _loan;
  mapping ( address => uint256) _taken;


    event OpenLoan(address indexed who, uint256 indexed amount, uint256 indexed id);
    event CloseLoan(address indexed who, uint256 indexed id);

    constructor (IERC20 paycoin) public {
      require(address(paycoin) != address(0), "Challenge: PayCoin is the zero address");

      _owner = _msgSender();
      _paycoin = paycoin;
      uint256 year = 2020;
      _end = year.timestampFromDateTime(6, 30, 16, 0, 0);
    }

    function changeEnd(uint256 end) external onlyManager {
      _end = end;
    }

    function openLoan(uint256 amount) external onlyCustomer returns (uint256){
      require( amount <= _max_loan.sub( _taken[_msgSender()] ), "Lender: you cannot ask more than 250 000 PaC total.");

      _taken[_msgSender()] = _taken[_msgSender()].add(amount);
      uint256 id = _id_Loan();
      _loan[_msgSender()][id]._open = true;
      _loan[_msgSender()][id]._amount = amount;
      _loan[_msgSender()][id]._block = block.number;

      _deliverCoins(_msgSender(), amount);
      emit OpenLoan(_msgSender(), amount, id);
      return id;
    }


    function closeLoan(uint256 id_loan) external onlyCustomer {
      require( now < _end, "Lender: time up.");
      require( _loan[_msgSender()][id_loan]._open, "Lender: loan closed.");

      ( , uint256 _fee_to_pay) = _loanStatus(id_loan);
      require( _paycoin.allowance(_msgSender(), address(this)) >=  (_loan[_msgSender()][id_loan]._amount).add(_fee_to_pay), "Challenge: allowance is not enough to close the loan.");

      _burnCoins(_msgSender(), _paycoin.allowance(_msgSender(), address(this)));
      _loan[_msgSender()][id_loan]._open = false;

      emit CloseLoan(_msgSender(), id_loan);
    }

    function loanStatus(uint256 id_loan) external view returns (uint256, uint256) {
      return _loanStatus(id_loan);
    }

    function _loanStatus(uint256 id_loan) internal view returns (uint256, uint256) {
      require( _loan[_msgSender()][id_loan]._open, "Lender: loan closed.");

      uint256 steps = block.number.sub( _loan[_msgSender()][id_loan]._block).div(500);
      uint256 _fee_to_pay = (_loan[_msgSender()][id_loan]._amount).mul(steps).div(1000);

      return (_loan[_msgSender()][id_loan]._amount, _fee_to_pay);
    }

    // Mint e Burn PayCoin
    function _burnCoins(address beneficiary, uint256 payAmount) internal {
      require(
          ERC20Burnable(address(_paycoin)).burnFrom(beneficiary, payAmount),
              "Challenge: burning PayCoin failed"
      );
    }

    function _deliverCoins(address beneficiary, uint256 payAmount) internal {
        require(
            ERC20Mintable(address(_paycoin)).mint(beneficiary, payAmount),
                "Challenge: minting PayCoin failed"
        );
    }

    // Generate random uint256
    function _id_Loan() internal returns (uint256) {
        _nonce += 1;
        return uint256(keccak256(abi.encodePacked(_nonce, _msgSender(), blockhash(block.number - 1))));
    }

    function close() public onlyManager {
      selfdestruct(_owner);
    }

}
