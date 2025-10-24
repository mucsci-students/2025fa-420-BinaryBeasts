#This test should always pass and is here to verify that the pytest runs in CI/CD pipelines.
#(pytest will fail the job if no tests are found)
def test_ci():
    assert(True)