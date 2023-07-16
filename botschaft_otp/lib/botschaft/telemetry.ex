defmodule Botschaft.Telemetry do
  use Agent

  def start_link(_args) do
    data = %{
      metrics: %{
        "botschaft.message" => 0,
        "botschaft.message.error" => 0,
        "botschaft.message.success" => 0,
        "botschaft.message.discord" => 0,
        "botschaft.message.telegram" => 0,
        "botschaft.message.discord.error" => 0,
        "botschaft.message.discord.success" => 0,
        "botschaft.message.telegram.error" => 0,
        "botschaft.message.telegram.success" => 0,
      }
    }
    agent = Agent.start_link(fn -> data end, name: __MODULE__)
    :telemetry.attach(__MODULE__, [:botschaft, :message, :sent], &handle_event/4, nil)
    agent
  end

  def handle_event(
    [:botschaft, :message, :sent],
    _measurements,
    %{provider: provider, destination: _destination, success: success?} = metadata,
    _config
  ) when is_boolean(success?) do
    Agent.update(__MODULE__, fn state ->
      state
      |> inc("botschaft.message")
      |> inc("botschaft.message.#{provider}")
      |> inc("botschaft.message.#{provider}.#{if success?, do: "success", else: "error"}")
    end)
  end

  def inc(state, key) do
    {_, state} = get_and_update_in(state, [:metrics, key], &{&1, &1 + 1})
    state
  end
end
