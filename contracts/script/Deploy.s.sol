// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.24;

import {Script, console} from "forge-std/Script.sol";
import {VerdictRegistry} from "../src/VerdictRegistry.sol";

contract DeployVerdictRegistry is Script {
    function run() external returns (VerdictRegistry registry) {
        uint256 deployerKey = vm.envUint("ARBITRUM_PRIVATE_KEY");

        vm.startBroadcast(deployerKey);
        registry = new VerdictRegistry();
        vm.stopBroadcast();

        console.log("VerdictRegistry deployed to:", address(registry));
        console.log("Owner:", registry.owner());
    }
}
