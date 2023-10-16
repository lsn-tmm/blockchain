pragma solidity ^0.5.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20Mintable.sol";
import "../ERC20/ERC20Burnable.sol";

import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import "@openzeppelin/contracts/math/SafeMath.sol";
import "../Utils/time/BokkyPooBahsDateTimeLibrary.sol";

import "./IExchangeAMPM.sol";
import "../Utils/roles/ManagerRole.sol";
import "../Utils/roles/CustomerRole.sol";

contract ExchangeAMPM is ManagerRole, CustomerRole {
  using SafeMath for uint256;
  using SafeERC20 for IERC20;
  using BokkyPooBahsDateTimeLibrary for uint256;

  // The token being sold
  IERC20 private _token;
  IERC20 private _paycoin;

  address payable private _owner;

  // Address where tokens are collected
  address private _tokenWallet;

  uint256[] _prices;

  uint256 private _start;
  uint256 private _end;

    //Events
    event Buy(address indexed buyer, uint256 indexed amount, uint256 indexed price);
    event Sell(address indexed buyer, uint256 indexed amount, uint256 indexed price);
    event PriceChange(address indexed addres, uint256 indexed id_price, uint256 indexed price);
    event ChangeStart(address indexed who, uint256 indexed when);
    event ChangeEnd(address indexed who, uint256 indexed when);


    constructor (uint256 price, IERC20 paycoin, IERC20 token) public {
        require(price > 0, "Exchange: price is 0");
        require(address(paycoin) != address(0), "Exchange: PayCoin is the zero address");
        require(address(token) != address(0), "Exchange: token is the zero address");

        _owner = _msgSender();
        _prices.push(price);
        _tokenWallet = _msgSender();
        _paycoin = paycoin;
        _token = token;

        uint year = 2020;
        _start = year.timestampFromDateTime(6, 24, 7, 0, 0);
        _end = year.timestampFromDateTime(6, 30, 16, 0, 0);
    }

    function set_PayCoin(IERC20 paycoin) external onlyManager {
      _paycoin = paycoin;
    }

    function set_AMPM(IERC20 token) external onlyManager {
      _token = token;
    }

    function changeStart(uint256 start) external onlyManager {
      _start = start;
      emit ChangeStart(_msgSender(), start);
    }

    function changeEnd(uint256 end) external onlyManager {
      _end = end;
      emit ChangeEnd(_msgSender(), end );
    }

    function isOpen() external view returns (bool){
      return _isOpen();
    }

    function _isOpen() internal view returns (bool){
      return ( now.getHour() >= 7 && now.getHour() < 16 );
    }

    function lastPrice() external view returns (uint256, uint256) {
            return _lastPrice();
    }

    function _lastPrice() internal view returns (uint256, uint256) {
      return (_prices.length.sub(1), _prices[_prices.length.sub(1)]);
    }

    function getHistory(uint256 _id_prezzo) external view returns (uint256) {
      (uint256 last_id, ) = _lastPrice();
      require( _id_prezzo <= last_id, "Exchange: id greater than the last registerd.");
      return _prices[_id_prezzo];
    }

    function priceChange(int256 difference) external onlyManager returns (uint256) {
      uint256 new_price;
      uint256 new_id;
      if (difference >= 0) new_price = _prices[_prices.length.sub(1)].add(uint256(difference));
      else new_price = _prices[_prices.length.sub(1)].sub(uint256(-difference));
      _prices.push(new_price);
      new_id = _prices.length.sub(1);

      emit PriceChange(address(this), new_id, new_price);
      return _prices.length.sub(1);
    }

    function buy(uint256 tknAmount) external onlyCustomer {
      require( now > _start && now < _end , "Exchange: not available.");
      require( _isOpen(), "Exchange: market closed."  );

      ( , uint256 price) = _lastPrice();
      uint256 final_price = tknAmount.mul( price ).div(10**18);
      _preValidatePurchase(_msgSender(), final_price);

      //update state
      _processPurchase(_msgSender(), tknAmount, final_price);
      emit Buy(_msgSender(), tknAmount, price);

    }

    function sell(uint256 tknAmount) external onlyCustomer {
      require( now > _start && now < _end, "Exchange: not available.");
      require( _isOpen(), "Exchange: market closed."  );
      _preValidateSale(_msgSender(), tknAmount);

      ( , uint256 price) = _lastPrice();
      uint256 final_price = tknAmount.mul( price ).div(10**18);

      //update state
      _processSale(_msgSender(), final_price.sub( final_price.mul(2).div(1000) ) );
      emit Sell(_msgSender(), tknAmount, price);

    }

    function _deliverTokens(address beneficiary, uint256 tokenAmount) internal {
        require(
            ERC20Mintable(address(_token)).mint(beneficiary, tokenAmount),
                "Exchange: minting token failed"
        );
    }

    function _deliverCoins(address beneficiary, uint256 payAmount) internal {
        require(
            ERC20Mintable(address(_paycoin)).mint(beneficiary, payAmount),
                "Exchange: minting PayCoin failed"
        );
    }

    function _burnTokens(address beneficiary, uint256 tokenAmount) internal {
      require(
          ERC20Burnable(address(_token)).burnFrom(beneficiary, tokenAmount),
              "Exchange: burning token failed"
      );
    }

    function _burnCoins(address beneficiary, uint256 payAmount) internal {
      require(
          ERC20Burnable(address(_paycoin)).burnFrom(beneficiary, payAmount),
              "Exchange: burning PayCoin failed"
      );
    }

    function _preValidatePurchase(address beneficiary, uint256 payAmount) internal view {
        require(beneficiary != address(0), "Exchange: beneficiary is the zero address");
        require( _paycoin.allowance(beneficiary, address(this)) >= payAmount.add( payAmount.mul(2).div(1000) ), "Exchange: not enough PayCoin allowed to purchase. (remeber Fee)");
        this; // silence state mutability warning without generating bytecode - see https://github.com/ethereum/solidity/issues/2691
    }

    function _preValidateSale(address beneficiary, uint256 tknAmount) internal view {
        require(beneficiary != address(0), "Exchange: beneficiary is the zero address");
	      require( _token.allowance(beneficiary, address(this)) >= tknAmount, "Exchange: not enough token allowed to sell.");
        this; // silence state mutability warning without generating bytecode - see https://github.com/ethereum/solidity/issues/2691
    }

    function _processPurchase(address beneficiary, uint256 tknAmount, uint256 payAmount) internal {
        _burnCoins(beneficiary, _paycoin.allowance(beneficiary, address(this)));
        _deliverCoins(_tokenWallet, payAmount);
        _deliverTokens(beneficiary, tknAmount);
    }

    function _processSale(address beneficiary, uint256 payAmount) internal {
        _burnTokens(beneficiary, _token.allowance(beneficiary, address(this)));
        _deliverCoins(beneficiary, payAmount);
    }

    function close() public onlyManager {
      selfdestruct(_owner);
    }

}
