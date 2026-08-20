import PageHeader from "../components/PageHeader";

export default function Pay() {
  return (
    <div>
      <PageHeader icon="💳" title="Pay Us" subtitle="Make payments securely for your orders and ID activation." />
      <div className="mx-auto max-w-3xl px-4 py-16">
        <div className="card p-8">
          <div className="grid gap-8 sm:grid-cols-2">
            <div>
              <h3 className="mb-3 font-bold text-herb-800">Bank Transfer</h3>
              <dl className="space-y-2 text-sm">
                <div className="flex justify-between"><dt className="text-herb-500">Account Name</dt><dd className="font-semibold">Arogyam Aradhya</dd></div>
                <div className="flex justify-between"><dt className="text-herb-500">Account No.</dt><dd className="font-semibold">XXXXXXXXXXXX</dd></div>
                <div className="flex justify-between"><dt className="text-herb-500">IFSC</dt><dd className="font-semibold">XXXX0000000</dd></div>
                <div className="flex justify-between"><dt className="text-herb-500">Bank</dt><dd className="font-semibold">—</dd></div>
              </dl>
            </div>
            <div className="text-center">
              <h3 className="mb-3 font-bold text-herb-800">UPI / QR</h3>
              <div className="mx-auto grid h-40 w-40 place-items-center rounded-2xl bg-herb-50 text-herb-300 ring-1 ring-herb-100">
                QR Code
              </div>
              <p className="mt-3 text-sm font-semibold text-herb-700">arogyamaradhya@upi</p>
            </div>
          </div>
          <div className="mt-8 rounded-xl bg-marigold-50 p-4 text-sm text-marigold-800 ring-1 ring-marigold-100">
            After payment, please share the transaction reference with your sponsor or on WhatsApp for quick confirmation.
          </div>
        </div>
      </div>
    </div>
  );
}
