defmodule Botschaft.Telemetry do
  use Agent

  def start_link(_args) do
    data = %{
      metrics: %{
        "botschaft.message" => 0,
        "botschaft.message.error" => 0,
        "botschaft.message.success" => 0
      }
    }

    agent = Agent.start_link(fn -> data end, name: __MODULE__)
    id = {__MODULE__, "botschaft.message.sent", self()}
    :telemetry.attach(id, [:botschaft, :message, :sent], &Botschaft.Telemetry.handle_event/4, nil)
    agent
  end

  def get_metrics() do
    Agent.get(__MODULE__, & &1[:metrics])
  end

  def handle_event(
        [:botschaft, :message, :sent],
        _measurements,
        %{provider: provider, destination: _destination, success: success?} = _metadata,
        _config
      )
      when is_boolean(success?) do
    success? = if success?, do: "success", else: "error"

    Agent.update(__MODULE__, fn state ->
      state
      |> inc("botschaft.message")
      |> inc("botschaft.message.#{success?}")
      |> inc("botschaft.message.#{provider}")
      |> inc("botschaft.message.#{provider}.#{success?}")
    end)
  end

  def inc(state, key) do
    {_, state} = get_and_update_in(state, [:metrics, key], &{&1, (&1 || 0) + 1})
    state
  end
end
