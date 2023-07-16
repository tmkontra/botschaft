defmodule Botschaft.Providers.Discord do
  use GenServer

  def start_link([config]) do
    args = config.(:discord)
    GenServer.start_link(__MODULE__, %{args: args, config: config}, name: __MODULE__)
  end

  def get_config() do
    GenServer.call(__MODULE__, :config)
  end

  def reload_config() do
    GenServer.cast(__MODULE__, :reload)
  end

  def send(destination, message) when is_binary(message) do
    GenServer.call(__MODULE__, {:message, %{destination: destination, text: message}})
  end

  def init(%{} = state) do
    {:ok, state}
  end

  def handle_call({:message, %{destination: name, text: text}}, _from, %{args: args} = state) do
    case Map.get(args, name) do
      %{"webhook_url" => webhook_url} ->
        case send_message(webhook_url, text) do
          :ok ->
            {:reply, :ok, state}
          {:error, reason} ->
            {:reply, {:error, reason}, state}
        end
      nil ->
        {:reply, {:error, "No discord destination #{name}"}, state}
    end
  end

  def handle_cast(:reload, %{config: config}) do
    {:noreply, %{args: config.(:discord), config: config}}
  end

  defp send_message(webhook_url, text) do
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
