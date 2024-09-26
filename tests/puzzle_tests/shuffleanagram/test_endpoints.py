from fastapi import status
from fastapi.testclient import TestClient

PREFIX = "/puzzles"

# I'm using the fixture known_puzzle_and_subpuzzle_names to parametrize the tests
# so that any test added to the router will be automatically tested.
# Each time that known_puzzle_and_subpuzzle_names is used, it's as if I were using
# @pytest.mark.parametrize(["puzzle_name", "subpuzzle_name"], [...])

# To make it easier to remember that using the fixture is the same as parametrizing,
# I'm putting _parametrized at the end of the test name


class TestShuffleAnagram:
    def test_index_parametrized(
        self, mock_init_client: TestClient, known_puzzle_and_subpuzzle_names: tuple[str, str]
    ) -> None:
        puzzle_name, _ = known_puzzle_and_subpuzzle_names
        response = mock_init_client.get(f"{PREFIX}/{puzzle_name}")
        assert response.status_code == status.HTTP_200_OK

    def test_get_shuffled_word_parametrized(
        self,
        mock_init_client: TestClient,
        known_puzzle_and_subpuzzle_names: tuple[str, str],
    ) -> None:
        # a downside of using dependencies is that they are not easily mocked,
        # I'd have to override the dependency in the mock__init_client fixture

        puzzle_name, _ = known_puzzle_and_subpuzzle_names
        response = mock_init_client.get(f"{PREFIX}/{puzzle_name}/shuffled")
        assert response.status_code == status.HTTP_200_OK
        assert hasattr(response, "context")
        assert "scrambled_word" in response.context  # type: ignore

    def test_get_static_files_parametrized(
        self,
        mock_init_client: TestClient,
        known_puzzle_and_subpuzzle_names: tuple[str, str],
    ) -> None:
        puzzle_name, _ = known_puzzle_and_subpuzzle_names
        response = mock_init_client.get(f"{PREFIX}/{puzzle_name}/static/styles.css")
        assert response.status_code == status.HTTP_200_OK

    def test_get_static_files_not_found_parametrized(
        self,
        mock_init_client: TestClient,
        known_puzzle_and_subpuzzle_names: tuple[str, str],
    ) -> None:
        puzzle_name, _ = known_puzzle_and_subpuzzle_names
        response = mock_init_client.get(f"{PREFIX}/{puzzle_name}/static/foo.bar")
        assert "404" in response.content.decode("utf-8")
        # TODO: change to next line if the custom_exception_handler is updated to return a 404 status
        # assert response.status_code == status.HTTP_404_NOT_FOUND
