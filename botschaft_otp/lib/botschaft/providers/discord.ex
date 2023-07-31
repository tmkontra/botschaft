defmodule Botschaft.Providers.Discord do
  use GenServer

  def start_link([get_config]) do
    config = get_config.(:discord)
    GenServer.start_link(__MODULE__, %{config: config, get_config: get_config}, name: __MODULE__)
  end

  def reload_config() do
    GenServer.cast(__MODULE__, :reload)
  end

  def send(destination, message) when is_binary(message) do
    GenServer.call(__MODULE__, {:message, %{destination: destination, message: %{text: message}}})
  end

  def send(destination, %{message: _text, template: _template} = message) do
    GenServer.call(__MODULE__, {:message, %{destination: destination, message: message}})
  end

  def init(%{} = state) do
    {:ok, state}
  end

  def handle_call({:message, %{destination: name, message: message}}, _from, %{config: %{vars: shared_vars} = config} = state) do
    case get_destination(name, config) do
      %{"webhook_url" => webhook_url} ->
        case send_message(webhook_url, message) do
          :ok ->
            :telemetry.execute([:botschaft, :message, :sent], %{}, %{provider: "discord", destination: name, success: true})
            {:reply, :ok, state}
          {:error, reason} ->
            :telemetry.execute([:botschaft, :message, :sent], %{}, %{provider: "discord", destination: name, success: false})
            {:reply, {:error, reason}, state}
        end
      nil ->
        {:reply, {:error, "No discord destination #{name}"}, state}
    end
  end

  def handle_cast(:reload, %{get_config: get_config}) do
    {:noreply, %{config: get_config.(:discord), get_config: get_config}}
  end

  defp get_destination(name, %{destinations: dests} = _config) do
    Map.get(dests, name)
  end

  defp send_message(webhook_url, %{text: text}) do
    IO.puts "sending message to discord: #{text} @ #{webhook_url}"
    body = %{content: text}
    # https://discord.com/developers/docs/resources/webhook#execute-webhook
    resp = Req.post!(webhook_url, json: body, params: [wait: "true"])
    if resp.status != 200 do
      {:error, "Failed to send message: #{inspect resp}"}
    else
      :ok
    end
  end

end
