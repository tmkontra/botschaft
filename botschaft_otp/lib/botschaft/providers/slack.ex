defmodule Botschaft.Providers.Slack do
  use GenServer

  def start_link([get_provider_config]) do
    config = get_provider_config.(:slack)
    GenServer.start_link(__MODULE__, %{config: config, get_config: get_provider_config}, name: __MODULE__)
  end

  def reload_config() do
    GenServer.cast(__MODULE__, :reload)
  end

  def send(destination, %Botschaft.Message{} = message) do
    GenServer.call(__MODULE__, {:message, %{destination: destination, message: message}})
  end

  def init(%{} = state) do
    {:ok, state}
  end

  def handle_call({:message, %{destination: name, message: message}}, _from, %{config: %{vars: shared_vars} = config} = state) do
    case Botschaft.Config.ProviderConfig.get_destination_config(config, name) do
      %{"incoming_webhook_url" => url, "vars" => vars} ->
        vars = Map.merge(shared_vars, vars)
        message = Botschaft.Message.render(message, vars)
        case send_webhook(url, message) do
          :ok ->
            :telemetry.execute([:botschaft, :message, :sent], %{}, %{provider: "slack", destination: name, success: true})
            {:reply, :ok, state}
          {:error, reason} ->
            :telemetry.execute([:botschaft, :message, :sent], %{}, %{provider: "slack", destination: name, success: false})
            {:reply, {:error, reason}, state}
        end
      nil ->
        {:reply, {:error, "No slack destination #{name}"}, state}
      _ ->
        {:reply, {:error, "Slack destination #{name} has unsupported configuration"}, state}
    end
  end

  def handle_cast(:reload, %{get_config: get_config}) do
    {:noreply, %{config: get_config.(:telegram), get_config: get_config}}
  end

  def send_webhook(url, message) do
    reply = Botschaft.Http.Client.post(url, %{
      "text" => message
    })
    if reply.status != 200 do
      {:error, "webhook rejected"}
    else
      :ok
    end
  end

end
