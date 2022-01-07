// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract FundMe {
    address private constant RINKEBY_AGGREGATOR_INTERFACE_ADDRESS = 0x8A753747A1Fa494EC906cE90E9f37563A8AF630e;

    mapping(address => uint256) public addressToAmountFunded;
    address[] public funders; 
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner {
        require(msg.sender == owner, "Allowed only for owner");
        _;
    }

    function fund() public payable {
        uint256 minimumUsd = 50 * 10 ** 18; // 50$
        require(getConversionRate(msg.value) >= minimumUsd, "You need to spend more ETH!");
        
        addressToAmountFunded[msg.sender] += msg.value;
        funders.push(msg.sender);
    }

    function getVersion() public view returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(RINKEBY_AGGREGATOR_INTERFACE_ADDRESS);
        return priceFeed.version();
    }

    function getPrice() public view returns(uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(RINKEBY_AGGREGATOR_INTERFACE_ADDRESS);
        (,int256 answer,,,) = priceFeed.latestRoundData();
        
        return uint256(answer * 10000000000);
    }

    function getConversionRate(uint256 ethAmount) public view returns(uint256) {
        uint256 ethPrice = getPrice();
        uint256 ethAmountInUsd = (ethPrice * ethAmount) / 1000000000000000000;

        return ethAmountInUsd;
    }

    function withdraw() payable onlyOwner public {
        payable(msg.sender).transfer(address(this).balance);
        
        for (uint256 funderIndex=0; funderIndex < funders.length; funderIndex++){
            address funder = funders[funderIndex];
            addressToAmountFunded[funder] = 0;
        }
        funders = new address[](0);
    }
}