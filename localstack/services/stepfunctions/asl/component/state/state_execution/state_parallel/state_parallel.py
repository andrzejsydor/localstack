from localstack.aws.api.stepfunctions import (
    HistoryEventExecutionDataDetails,
    HistoryEventType,
    StateEnteredEventDetails,
    StateExitedEventDetails,
)
from localstack.services.stepfunctions.asl.component.state.state_execution.execute_state import (
    ExecutionState,
)
from localstack.services.stepfunctions.asl.component.state.state_execution.state_parallel.branches_decl import (
    BranchesDecl,
)
from localstack.services.stepfunctions.asl.component.state.state_props import StateProps
from localstack.services.stepfunctions.asl.eval.environment import Environment
from localstack.services.stepfunctions.asl.utils.encoding import to_json_str


class StateParallel(ExecutionState):
    # Branches (Required)
    # An array of objects that specify state machines to execute in state_parallel. Each such state
    # machine object must have fields named States and StartAt, whose meanings are exactly
    # like those in the top level of a state machine.
    branches: BranchesDecl

    def __init__(self):
        super().__init__(
            state_entered_event_type=HistoryEventType.ParallelStateEntered,
            state_exited_event_type=HistoryEventType.ParallelStateExited,
        )

    def _get_state_entered_event_details(self, env: Environment) -> StateEnteredEventDetails:
        return StateEnteredEventDetails(
            name=self.name,
            input=to_json_str(env.inp, separators=(",", ":")),
            inputDetails=HistoryEventExecutionDataDetails(
                truncated=False  # Always False for api calls.
            ),
        )

    def _get_state_exited_event_details(self, env: Environment) -> StateExitedEventDetails:
        return StateExitedEventDetails(
            name=self.name,
            output=to_json_str(env.inp, separators=(",", ":")),
            outputDetails=HistoryEventExecutionDataDetails(
                truncated=False  # Always False for api calls.
            ),
        )

    def from_state_props(self, state_props: StateProps) -> None:
        super(StateParallel, self).from_state_props(state_props)
        self.branches = state_props.get(
            typ=BranchesDecl,
            raise_on_missing=ValueError(f"Missing Branches definition in props '{state_props}'."),
        )

    def _eval_execution(self, env: Environment) -> None:
        env.event_history.add_event(
            hist_type_event=HistoryEventType.ParallelStateStarted,
        )
        self.branches.eval(env)
        env.event_history.add_event(hist_type_event=HistoryEventType.ParallelStateSucceeded)
