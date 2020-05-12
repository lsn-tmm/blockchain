// Version of Solidity compiler this program was written for
pragma solidity ^0.5.0;

// Our first contract is a faucet
contract FaucetAdvanced{

  mapping(address => uint256) internal balance;
  //uint256 private max_withdraw = 1000000000000000000;
  address private owner = msg.sender;

  event Refilled(address indexed owner, address indexed recipient, uint256 amount);

    // Give out ether to anyone who asks
    function withdraw(uint withdraw_amount) public {
        // Check if the account is registered
        require( balance[msg.sender] != 0, 'Address not registered.' );
        // Limit withdrowal amount
        require (withdraw_amount <= balance[msg.sender], 'Not enough ether to withdraw.' );
        // Send the amount to the address that requested it
        msg.sender.transfer(withdraw_amount);
        balance[msg.sender] = balance[msg.sender] - withdraw_amount;
    }

    //function () external payable{ require( msg.sender == owner, 'Only the owner can tranfer.' ); }
    /*
    function addAccount(address account) external returns (bool){
      require( balance[account] == 0 , 'Account already registered.');
      balance[account] = max_withdraw;
      return true;
    }
    */

    function available(address account) external view returns (uint256){
        return balance[account];
    }

    function refill(address account) external payable returns (bool){
        require( msg.sender == owner, 'Only the owner can refill.' );
        balance[account] = balance[account] + msg.value;
        emit Refilled(msg.sender, account, msg.value);
        return true;
    }
}
