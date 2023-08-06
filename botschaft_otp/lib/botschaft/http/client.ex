defmodule Botschaft.Http.Client do
  alias Req

  def get(url, params \\ []) do
    Req.get!(url, params: params)
  end

  def post(url, body, params \\ []) do
    Req.post!(url, json: body, params: params)
  end
end
