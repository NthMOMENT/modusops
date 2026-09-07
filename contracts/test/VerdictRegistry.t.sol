// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.24;

import {Test, console} from "forge-std/Test.sol";
import {VerdictRegistry} from "../src/VerdictRegistry.sol";

contract VerdictRegistryTest is Test {
    VerdictRegistry public registry;
    address public deployer = address(this);

    function setUp() public {
        registry = new VerdictRegistry();
    }

    // -----------------------------------------------------------------------
    // Happy path
    // -----------------------------------------------------------------------

    function test_commitVerdict_basic() public {
        bytes32 hash = keccak256(abi.encodePacked("test-verdict-json"));

        vm.expectEmit(false, true, true, true);
        emit VerdictRegistry.VerdictLogged(
            "OBE-2026-001",
            hash,
            VerdictRegistry.VerdictType.ESCALATE,
            74,
            VerdictRegistry.Jurisdiction.FEDERAL,
            block.timestamp,
            deployer
        );

        uint256 idx = registry.commitVerdict(
            "OBE-2026-001",
            hash,
            VerdictRegistry.VerdictType.ESCALATE,
            74,
            VerdictRegistry.Jurisdiction.FEDERAL
        );

        assertEq(idx, 1);
        assertEq(registry.verdictCount(), 1);
        assertTrue(registry.caseExists("OBE-2026-001"));
    }

    function test_getVerdictByIndex() public {
        bytes32 hash = keccak256(abi.encodePacked("verdict-data"));
        registry.commitVerdict(
            "CASE-001",
            hash,
            VerdictRegistry.VerdictType.PROCEED,
            85,
            VerdictRegistry.Jurisdiction.STATE
        );

        VerdictRegistry.VerdictRecord memory r = registry.getVerdictByIndex(1);
        assertEq(r.caseId, "CASE-001");
        assertEq(r.verdictHash, hash);
        assertEq(uint8(r.verdict), uint8(VerdictRegistry.VerdictType.PROCEED));
        assertEq(r.confidenceScore, 85);
        assertEq(uint8(r.jurisdiction), uint8(VerdictRegistry.Jurisdiction.STATE));
        assertEq(r.agentTokens[0], 1416);
        assertEq(r.agentTokens[1], 1417);
        assertEq(r.agentTokens[2], 1418);
        assertEq(r.agentTokens[3], 1419);
    }

    function test_getVerdictByCaseId() public {
        bytes32 hash = keccak256(abi.encodePacked("by-case-id"));
        registry.commitVerdict(
            "CASE-002",
            hash,
            VerdictRegistry.VerdictType.DISMISS,
            30,
            VerdictRegistry.Jurisdiction.LOCAL
        );

        VerdictRegistry.VerdictRecord memory r = registry.getVerdictByCaseId("CASE-002");
        assertEq(r.caseId, "CASE-002");
        assertEq(r.confidenceScore, 30);
    }

    function test_multipleVerdicts() public {
        registry.commitVerdict("C-001", bytes32(0), VerdictRegistry.VerdictType.PROCEED, 90, VerdictRegistry.Jurisdiction.FEDERAL);
        registry.commitVerdict("C-002", bytes32(0), VerdictRegistry.VerdictType.DISMISS, 10, VerdictRegistry.Jurisdiction.LOCAL);
        registry.commitVerdict("C-003", bytes32(0), VerdictRegistry.VerdictType.REVIEW,  50, VerdictRegistry.Jurisdiction.STATE);

        assertEq(registry.verdictCount(), 3);
    }

    // -----------------------------------------------------------------------
    // Revert cases
    // -----------------------------------------------------------------------

    function test_revert_unauthorized() public {
        address attacker = address(0xBAD);
        vm.prank(attacker);
        vm.expectRevert(VerdictRegistry.Unauthorized.selector);
        registry.commitVerdict("HACK-001", bytes32(0), VerdictRegistry.VerdictType.PROCEED, 50, VerdictRegistry.Jurisdiction.LOCAL);
    }

    function test_revert_duplicateCaseId() public {
        registry.commitVerdict("DUP-001", bytes32(0), VerdictRegistry.VerdictType.PROCEED, 50, VerdictRegistry.Jurisdiction.LOCAL);
        vm.expectRevert(abi.encodeWithSelector(VerdictRegistry.CaseAlreadyExists.selector, "DUP-001"));
        registry.commitVerdict("DUP-001", bytes32(0), VerdictRegistry.VerdictType.DISMISS, 20, VerdictRegistry.Jurisdiction.LOCAL);
    }

    function test_revert_invalidConfidenceScore() public {
        vm.expectRevert(abi.encodeWithSelector(VerdictRegistry.InvalidConfidenceScore.selector, 101));
        registry.commitVerdict("BAD-SCORE", bytes32(0), VerdictRegistry.VerdictType.PROCEED, 101, VerdictRegistry.Jurisdiction.LOCAL);
    }

    function test_revert_emptyCaseId() public {
        vm.expectRevert(VerdictRegistry.EmptyCaseId.selector);
        registry.commitVerdict("", bytes32(0), VerdictRegistry.VerdictType.PROCEED, 50, VerdictRegistry.Jurisdiction.LOCAL);
    }

    // -----------------------------------------------------------------------
    // Edge cases
    // -----------------------------------------------------------------------

    function test_confidenceScore_boundaries() public {
        registry.commitVerdict("SCORE-0",   bytes32(0), VerdictRegistry.VerdictType.DISMISS,  0,   VerdictRegistry.Jurisdiction.LOCAL);
        registry.commitVerdict("SCORE-100", bytes32(0), VerdictRegistry.VerdictType.PROCEED,  100, VerdictRegistry.Jurisdiction.FEDERAL);
        assertEq(registry.verdictCount(), 2);
    }

    function test_caseExists_false_for_unknown() public {
        assertFalse(registry.caseExists("NONEXISTENT"));
    }
}
