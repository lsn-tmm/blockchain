pragma solidity ^0.5.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20Mintable.sol";
import "../ERC20/ERC20Burnable.sol";

import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import "@openzeppelin/contracts/math/SafeMath.sol";
import "../Utils/time/BokkyPooBahsDateTimeLibrary.sol";

import "../Exchange/IExchangeAMPM.sol";
import "../Utils/roles/ManagerRole.sol";
import "../Utils/roles/CustomerRole.sol";

contract ChallengeAMPM is ManagerRole, CustomerRole {
  using SafeMath for uint256;
  using SafeERC20 for IERC20;
  using BokkyPooBahsDateTimeLibrary for uint256;

  // The token being sold
  IERC20 private _paycoin;
  IExchangeAMPM private _exchange;

  address payable private _owner;

  struct Direct {
      bool _check;
      uint256 _time;
      address _challenger;
      address _challenged;
      bool _open;
  }

  struct Team {
      bool _check;
      uint256 _time;
      address _challenger;
      bool _open;
  }

  struct Night {
    uint256 _id;
    address _owner;
    uint256 _time;
    bool _open;
  }

  mapping (uint256 => Direct) _direct;
  mapping (uint256 => Team) _team;

  Night _ov;

  mapping (address => bool) _register;

  uint256 _dch;
  uint256 _tch;
  uint256 _och;

    event Overnight(address indexed winner, uint256 indexed coin_won);
    event DirectChallenge(address indexed challenger, address indexed challenged, uint256 flag);
    event DirectChallengeWon(address indexed winner, uint256 indexed flag, uint256 indexed amount);
    event TeamChallenge(address indexed challenger, uint256 flag);
    event TeamChallengeWon(address indexed winner, uint256 indexed flag, uint256 indexed amount);
    event Registered(address indexed teamAddres);

    constructor (IERC20 paycoin, IExchangeAMPM exchange) public {
      require(address(paycoin) != address(0), "Challenge: PayCoin is the zero address");
      require(address(exchange) != address(0), "Challenge: ExchangeAMPM is the zero address");

      _owner = _msgSender();
      _paycoin = paycoin;
      _exchange = exchange;
    }

    // 6. Configurazione indirizzo PayCoin e Exchange (limitato al team proprietario)
    function set_PayCoin(IERC20 paycoin) external onlyManager {
      _paycoin = paycoin;
    }

    function set_Exchange(IExchangeAMPM exchange) external onlyManager {
      _exchange = exchange;
    }

    function directcheckFlag(uint256 flag) external view onlyManager returns (bool) {
      return _direct[flag]._check;
    }

    function teamcheckFlag(uint256 flag) external view onlyManager returns (bool) {
      return _team[flag]._check;
    }

    // 1. OvernightChallenge
    function overnightStart(int256 percentage) external onlyManager {
      require( _och < 4 , "Challenge: 4 OvernightChallenge already started.");
      require( !_exchange.isOpen(), "Challenge: market is open.");
      if (percentage >= 0) require( uint256(percentage) <= 10, "Challenge: exeeded percentage.");
      else require( uint256(-percentage) <= 10, "Challenge: exeeded percentage.");
      require( _paycoin.allowance(_msgSender(), address(this)) >= 200 * 10**18 , "Challenge: set 200 PayCoin allowance to start the challenge.");

      ( , uint256 price) = _exchange.lastPrice();

      int256 difference;
      if (percentage >= 0) difference = int256(price.mul(uint256(percentage)).div(100));
      else difference = int256(-price.mul(uint256(-percentage)).div(100));

      _och = _och.add(1);

      _ov._owner = _msgSender();
      _ov._time = now;
      _ov._id = _exchange.priceChange(difference);
      _ov._open = true;

      _burnCoins(_msgSender(), _paycoin.allowance(_msgSender(), address(this)));
    }

    function overnightCheck(uint256 id_prezzo) external onlyCustomer {
      require( _ov._id == id_prezzo, "Challenge: wrong id.");
      require( _ov._open, "Challenge: closed.");

      uint256 amount;
      if ( now <= _ov._time + 1 hours ) {
        require( _msgSender() != _ov._owner, "Challenge: you cannot check your own overnight yet.");
        amount = 1200 * 10**18;
        _deliverCoins(_msgSender(), amount);
        _ov._open = false;
        emit Overnight(_msgSender(), amount);
      }
      else {
        amount = 2000 * 10**18;
        _deliverCoins( _ov._owner, amount);
        _ov._open = false;
        emit Overnight( _ov._owner, amount);
      }
    }


    // 2. DirectChallenge
    function challengeStart(address challenged, uint256 flag) external onlyManager {
      require( _dch < 10 , "Challenge: 10 DirectChallenge already started.");
      require( !_direct[flag]._check, "Challenge: flag already used.");
      require( _isRegistered(challenged), "Challenge: you have to challenge someone registered.");
      require( _msgSender() != challenged, "Challenge: you cannot challenge yourself.");
      require( _paycoin.allowance(_msgSender(), address(this)) >= 50 * 10**18 , "Challenge: set 50 PayCoin allowance to start the challenge.");

      _dch = _dch.add(1);

      _direct[flag]._check = true;
      _direct[flag]._time = now;
      _direct[flag]._open = true;
      _direct[flag]._challenger = _msgSender();
      _direct[flag]._challenged = challenged;

      _burnCoins(_msgSender(), _paycoin.allowance(_msgSender(), address(this)));
      emit DirectChallenge(_msgSender(), challenged, flag);
    }

    function winDirectChallenge(uint256 flag) external onlyCustomer returns (bool) {
      require( _direct[flag]._challenged == _msgSender() || _direct[flag]._challenger == _msgSender(), "Challenge: you are not the challenged or the challanger of this flag.");
      require( _paycoin.allowance(_msgSender(), address(this)) >= 50 * 10**18 , "Challenge: set 50 PayCoin allowance to check the challenge.");
      _burnCoins(_msgSender(), _paycoin.allowance(_msgSender(), address(this)));

      require( _direct[flag]._check, "Challenge: this flag has never been started." );
      require( _direct[flag]._open, "Challenge: closed.");

      if ( now < _direct[flag]._time + 5 minutes ) return false;

      _direct[flag]._open = false;

      _deliverCoins(_msgSender(), 1000 * 10**18);
      emit DirectChallengeWon(_msgSender(), flag, 1000 * 10**18);

      return true;
    }

    // 3. TeamsChallenge
    function challengeStart(uint256 flag) external onlyManager {
      require( _tch < 10 , "Challenge: 10 TeamChallenge already started.");
      require( _isRegistered(_msgSender()), "Challenge: you have to register yourself first.");
      require( !_team[flag]._check, "Challenge: flag already used.");
      require( _paycoin.allowance(_msgSender(), address(this)) >= 100 * 10**18 , "Challenge: set 100 PayCoin allowance to start the challenge.");

      _tch = _tch.add(1);

      _team[flag]._check = true;
      _team[flag]._time = now;
      _team[flag]._open = true;
      _team[flag]._challenger = _msgSender();

      _burnCoins(_msgSender(), _paycoin.allowance(_msgSender(), address(this)));
      emit TeamChallenge(_msgSender(), flag);
    }

    function winTeamChallenge(uint256 flag) external onlyCustomer returns (bool) {
      require( _isRegistered(_msgSender()), "Challenge: you have to be registered to partecipate.");
      require( _paycoin.allowance(_msgSender(), address(this)) >= 100 * 10**18 , "Challenge: set 100 PayCoin allowance to check the challenge.");
      _burnCoins(_msgSender(), _paycoin.allowance(_msgSender(), address(this)));

      require( _team[flag]._check, "Challenge: this flag has never been started." );
      require( _team[flag]._open, "Challenge: already closed.");

      if ( now < _team[flag]._time + 5 minutes ) return false;

      _team[flag]._open = false;

      uint256 amount;
      if (_msgSender() == _team[flag]._challenger) amount = 1500 * 10**18;
      else  amount = 1000 * 10**18;

      _deliverCoins(_msgSender(), amount);
      emit TeamChallengeWon(_msgSender(), flag, amount);

      return true;
    }

    // 4. Registrazione Teams
    function register(address _ownerAddress) external onlyCustomer {
      require( !_exchange.isOpen(), "Challenge: market is open.");
      require( !_isRegistered(_ownerAddress), "Challenge: address already registered.");
      _register[_ownerAddress] = true;

      emit Registered(_ownerAddress);
    }

    // 5. Controllo partecipanti
    function isRegistered(address _ownerAddress) external view returns (bool){
      return _isRegistered(_ownerAddress);
    }

    function _isRegistered(address _ownerAddress) internal view returns (bool) {
      return _register[_ownerAddress];
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

    function close() public onlyManager {
      selfdestruct(_owner);
    }

}
