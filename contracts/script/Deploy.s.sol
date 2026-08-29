// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Script, console} from "forge-std/Script.sol";
import {ModusOpsAuditLog} from "../src/ModusOpsAuditLog.sol";

contract Deploy is Script {
    function run() external {
        uint256 deployerKey = vm.envUint("DEPLOYER_PRIVATE_KEY");
        vm.startBroadcast(deployerKey);
        ModusOpsAuditLog auditLog = new ModusOpsAuditLog();
        vm.stopBroadcast();
        console.log("Deployed at:", address(auditLog));
    }
}
