defmodule Botschaft.Topics do
  # A topic is an arbitrary list of destinations, which a message will be dispatched to.

  use GenServer

  def start_link([get_config]) when is_function(get_config, 0) do
    config = get_config.()
    GenServer.start_link(__MODULE__, %{config: config, get_config: get_config}, name: __MODULE__)
  end

  def reload_config() do
    GenServer.cast(__MODULE__, :reload)
  end

  def send(topic, message) do
    GenServer.call(__MODULE__, {:message, %{topic: topic, message: message}})
  end

  def init(%{} = state) do
    {:ok, state}
  end

  def handle_call({:message, %{topic: topic_name, message: message}}, _from, %{config: %{} = config} = state) do
    reply = case Map.get(config, topic_name) do
      nil ->
        {:error, "No such topic configured"}
      %{"destinations" => destinations} ->
        dispatch_message(destinations, message)
      _ ->
        {:error, "Topic misconfigured"}
    end
    {:reply, reply, state}
  end

  def handle_cast(:reload, %{get_config: get_config}) do
    {:noreply, %{config: get_config.(), get_config: get_config}}
  end

  defp dispatch_message(destinations, message) when is_list(destinations) do
    for destination <- destinations do
      {destination, send_message(destination, message)}
    end
  end

  defp send_message(destination, message) do
    [provider, destination] = String.split(destination, ".", parts: 2)
    IO.puts "sending to #{destination}"
    # TODO: get provider module by name and send message
    Botschaft.Providers.send_message(provider, destination, message)
  end
end
